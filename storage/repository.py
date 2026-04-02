from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlalchemy import select

from storage.db import get_session
from storage.models.checkpoint import ExecutionCheckpointRecord
from storage.models.execution import ExecutionLogRecord, ExecutionRecord
from storage.models.metrics import ExecutionMetricRecord
from storage.models.plugin import PluginRecord
from storage.models.plugin_capability import PluginCapabilityRecord
from storage.models.workflow import WorkflowRecord
from storage.models.workflow_version import WorkflowVersionRecord
from utils.ids import new_id
from utils.serialization import stable_json


class Repository:
    def create_workflow(self, workflow_id: str, name: str, definition: Dict[str, Any]) -> None:
        with get_session() as session:
            record = WorkflowRecord(
                id=workflow_id,
                name=name,
                definition_json=stable_json(definition),
            )
            session.add(record)
            session.commit()

    def create_workflow_id(self, name: str) -> str:
        return new_id("wf")

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            record = session.get(WorkflowRecord, workflow_id)
            if record is None:
                return None
            return {
                "id": record.id,
                "name": record.name,
                "definition": json.loads(record.definition_json),
            }

    def list_workflows(
        self,
        name_contains: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = select(WorkflowRecord)
            if name_contains:
                query = query.where(WorkflowRecord.name.contains(name_contains))
            records = session.scalars(query.offset(offset).limit(limit)).all()
            return [
                {
                    "id": record.id,
                    "name": record.name,
                    "definition": json.loads(record.definition_json),
                }
                for record in records
            ]

    def create_workflow_version(self, workflow_id: str, version: int, definition: Dict[str, Any]) -> None:
        with get_session() as session:
            record = WorkflowVersionRecord(
                workflow_id=workflow_id,
                version=version,
                definition_json=stable_json(definition),
            )
            session.add(record)
            session.commit()

    def list_workflow_versions(self, workflow_id: str) -> List[Dict[str, Any]]:
        with get_session() as session:
            records = session.scalars(
                select(WorkflowVersionRecord).where(WorkflowVersionRecord.workflow_id == workflow_id)
            ).all()
            return [
                {
                    "version": record.version,
                    "definition": json.loads(record.definition_json),
                    "created_at": record.created_at,
                }
                for record in records
            ]

    def create_execution(self, execution_id: str, workflow_id: str, status: str) -> None:
        with get_session() as session:
            record = ExecutionRecord(id=execution_id, workflow_id=workflow_id, status=status)
            session.add(record)
            session.commit()

    def update_execution(
        self,
        execution_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        finished_at: Optional[str] = None,
    ) -> None:
        with get_session() as session:
            record = session.get(ExecutionRecord, execution_id)
            if record is None:
                return
            record.status = status
            if result is not None:
                record.result_json = stable_json(result)
            if error is not None:
                record.error = error
            if finished_at is not None:
                record.finished_at = finished_at
            session.commit()

    def add_log(
        self,
        execution_id: str,
        node_id: str,
        status: str,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
    ) -> None:
        with get_session() as session:
            record = ExecutionLogRecord(
                execution_id=execution_id,
                node_id=node_id,
                status=status,
                output_json=stable_json(output) if output is not None else None,
                error=error,
                started_at=started_at,
                finished_at=finished_at,
            )
            session.add(record)
            session.commit()

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            record = session.get(ExecutionRecord, execution_id)
            if record is None:
                return None
            logs = session.scalars(
                select(ExecutionLogRecord).where(ExecutionLogRecord.execution_id == execution_id)
            ).all()
            return {
                "id": record.id,
                "workflow_id": record.workflow_id,
                "status": record.status,
                "started_at": record.started_at,
                "finished_at": record.finished_at,
                "result": json.loads(record.result_json) if record.result_json else None,
                "error": record.error,
                "logs": [log.to_dict() for log in logs],
            }

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with get_session() as session:
            query = select(ExecutionRecord)
            if workflow_id:
                query = query.where(ExecutionRecord.workflow_id == workflow_id)
            if status:
                query = query.where(ExecutionRecord.status == status)
            records = session.scalars(query).all()
            return [self.get_execution(record.id) for record in records if record is not None]

    def list_execution_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        with get_session() as session:
            logs = session.scalars(
                select(ExecutionLogRecord).where(ExecutionLogRecord.execution_id == execution_id)
            ).all()
            return [log.to_dict() for log in logs]

    def add_metric(self, execution_id: str, node_id: str, duration_ms: int, attempts: int) -> None:
        with get_session() as session:
            record = ExecutionMetricRecord(
                execution_id=execution_id,
                node_id=node_id,
                duration_ms=duration_ms,
                attempts=attempts,
            )
            session.add(record)
            session.commit()

    def list_metrics(self, execution_id: str) -> List[Dict[str, Any]]:
        with get_session() as session:
            records = session.scalars(
                select(ExecutionMetricRecord).where(ExecutionMetricRecord.execution_id == execution_id)
            ).all()
            return [
                {
                    "node_id": record.node_id,
                    "duration_ms": record.duration_ms,
                    "attempts": record.attempts,
                    "recorded_at": record.recorded_at,
                }
                for record in records
            ]

    def register_plugin(self, name: str, version: str, description: str) -> None:
        with get_session() as session:
            existing = session.get(PluginRecord, name)
            if existing is not None:
                return
            record = PluginRecord(name=name, version=version, description=description)
            session.add(record)
            session.commit()

    def register_plugin_capabilities(self, name: str, capabilities: List[str]) -> None:
        with get_session() as session:
            for capability in capabilities:
                record = PluginCapabilityRecord(plugin_name=name, capability=capability)
                session.add(record)
            session.commit()

    def list_plugin_capabilities(self, name: str) -> List[str]:
        with get_session() as session:
            records = session.scalars(
                select(PluginCapabilityRecord).where(PluginCapabilityRecord.plugin_name == name)
            ).all()
            return [record.capability for record in records]

    def get_plugin(self, name: str) -> Optional[Dict[str, Any]]:
        with get_session() as session:
            record = session.get(PluginRecord, name)
            if record is None:
                return None
            return record.to_dict()

    def list_plugins(self) -> List[Dict[str, Any]]:
        with get_session() as session:
            records = session.scalars(select(PluginRecord)).all()
            return [record.to_dict() for record in records]

    def save_execution_checkpoint(
        self,
        checkpoint_id: str,
        execution_id: str,
        node_id: str,
        status: str,
        outputs: Dict[str, Any],
    ) -> None:
        with get_session() as session:
            record = ExecutionCheckpointRecord(
                id=checkpoint_id,
                execution_id=execution_id,
                node_id=node_id,
                status=status,
                outputs_json=stable_json(outputs),
            )
            session.add(record)
            session.commit()

    def list_execution_checkpoints(self, execution_id: str) -> List[Dict[str, Any]]:
        with get_session() as session:
            records = session.scalars(
                select(ExecutionCheckpointRecord)
                .where(ExecutionCheckpointRecord.execution_id == execution_id)
                .order_by(ExecutionCheckpointRecord.created_at)
            ).all()
            return [record.to_dict() for record in records]
