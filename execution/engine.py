from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from cache.base import CacheBackend
from execution.context import ExecutionContext, ExecutionMetric
from execution.models import ExecutionResult, ExecutionStatus, NodeStatus
from execution.planner import ExecutionPlanner
from execution.policies import CachePolicy, RetryPolicy, TimeoutPolicy
from execution.scheduler import Scheduler
from plugins.registry import PluginRegistry
from execution.checkpoint import CheckpointManager
from storage.repository import Repository
from utils.errors import ExecutionError
from utils.ids import new_id
from utils.paths import get_in
from utils.serialization import stable_json


class WorkflowEngine:
    def __init__(self, repository: Repository, registry: PluginRegistry, cache: CacheBackend) -> None:
        self._repository = repository
        self._registry = registry
        self._cache = cache
        self._planner = ExecutionPlanner()
        self._scheduler = Scheduler()

    async def run_workflow(
        self,
        workflow_id: str,
        input_payload: Dict[str, Any],
        async_mode: bool = False,
        checkpoint: bool = False,
    ) -> ExecutionResult:
        workflow = self._repository.get_workflow(workflow_id)
        if workflow is None:
            raise ExecutionError("Workflow not found")
        execution_id = new_id("exec")
        self._repository.create_execution(execution_id, workflow_id, ExecutionStatus.PENDING.value)
        self._repository.update_execution(execution_id, ExecutionStatus.RUNNING.value)

        try:
            context = ExecutionContext(
                execution_id=execution_id,
                workflow_id=workflow_id,
                input_payload=input_payload,
                async_mode=async_mode,
            )
            result = await self._execute_nodes(
                context,
                workflow["definition"]["nodes"],
                checkpoint=checkpoint,
            )
            self._repository.update_execution(
                execution_id,
                ExecutionStatus.SUCCEEDED.value,
                result=result,
                finished_at=datetime.utcnow().isoformat(),
            )
            for metric in context.metrics:
                self._repository.add_metric(
                    execution_id=execution_id,
                    node_id=metric.node_id,
                    duration_ms=int(metric.duration_ms),
                    attempts=metric.attempts,
                )
            return ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=ExecutionStatus.SUCCEEDED,
                output=result,
                error=None,
            )
        except Exception as exc:  # noqa: BLE001
            self._repository.update_execution(
                execution_id,
                ExecutionStatus.FAILED.value,
                error=str(exc),
                finished_at=datetime.utcnow().isoformat(),
            )
            return ExecutionResult(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=ExecutionStatus.FAILED,
                output=None,
                error=str(exc),
            )

    async def _execute_nodes(
        self,
        context: ExecutionContext,
        nodes: List[Dict[str, Any]],
        checkpoint: bool = False,
    ) -> Dict[str, Any]:
        checkpoint_manager = CheckpointManager(self._repository) if checkpoint else None
        outputs: Dict[str, Any] = {}
        node_map = {node["id"]: node for node in nodes}
        plan = self._planner.build(nodes)

        async def runner(node_id: str) -> Dict[str, Any]:
            node = node_map[node_id]
            payload = {"input": context.input_payload, "node": node, "outputs": outputs}
            cache_policy = CachePolicy.from_node(node)
            cache_key = self._cache_key(
                workflow_id=context.workflow_id,
                node_id=node_id,
                payload=payload,
                cache_policy=cache_policy,
            )
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached
            result = await self._run_node(context, node, payload)
            ttl = cache_policy.ttl_seconds or 300
            self._cache.set(cache_key, result, ttl_seconds=ttl)
            if checkpoint_manager is not None:
                snapshot = dict(outputs)
                snapshot[node_id] = result
                checkpoint_manager.save(
                    execution_id=context.execution_id,
                    node_id=node_id,
                    status=NodeStatus.SUCCEEDED.value,
                    outputs=snapshot,
                )
            return result

        if context.async_mode:
            outputs = await self._scheduler.run(plan.stages, runner)
        else:
            for node_id in plan.linear_order():
                outputs[node_id] = await runner(node_id)

        return {"nodes": outputs}

    async def _run_node(
        self,
        context: ExecutionContext,
        node: Dict[str, Any],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        node_id = node["id"]
        plugin_name = node["plugin"]
        retry_policy = RetryPolicy.from_node(node)
        timeout_policy = TimeoutPolicy.from_node(node)
        self._repository.add_log(
            execution_id=context.execution_id,
            node_id=node_id,
            status=NodeStatus.RUNNING.value,
            started_at=datetime.utcnow().isoformat(),
        )

        attempts = 0
        while True:
            attempts += 1
            try:
                start = time.perf_counter()
                if timeout_policy.timeout_seconds is None:
                    result = await self._registry.run(plugin_name, self._merge_payload(node, payload))
                else:
                    result = await asyncio.wait_for(
                        self._registry.run(plugin_name, self._merge_payload(node, payload)),
                        timeout=timeout_policy.timeout_seconds,
                    )
                duration_ms = (time.perf_counter() - start) * 1000
                context.record_metric(
                    ExecutionMetric(node_id=node_id, duration_ms=duration_ms, attempts=attempts)
                )
                self._repository.add_log(
                    execution_id=context.execution_id,
                    node_id=node_id,
                    status=NodeStatus.SUCCEEDED.value,
                    output=result,
                    finished_at=datetime.utcnow().isoformat(),
                )
                return result
            except Exception as exc:  # noqa: BLE001
                self._repository.add_log(
                    execution_id=context.execution_id,
                    node_id=node_id,
                    status=NodeStatus.FAILED.value,
                    error=str(exc),
                    finished_at=datetime.utcnow().isoformat(),
                )
                if attempts >= retry_policy.max_attempts:
                    raise
                if retry_policy.backoff_seconds > 0:
                    await asyncio.sleep(retry_policy.backoff_seconds)

    def _merge_payload(self, node: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(payload)
        node_input = node.get("input") or {}
        merged.update(node_input)
        return merged

    def _cache_key(
        self,
        workflow_id: Optional[str],
        node_id: str,
        payload: Dict[str, Any],
        cache_policy: CachePolicy,
    ) -> str:
        if cache_policy.key_fields:
            filtered = {field: get_in(payload, field) for field in cache_policy.key_fields}
            fingerprint = stable_json(filtered)
        else:
            fingerprint = stable_json(payload)
        prefix = workflow_id or "workflow"
        return f"{prefix}:{node_id}:{fingerprint}"
