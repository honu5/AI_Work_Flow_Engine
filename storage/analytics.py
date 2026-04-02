from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from storage.repository import Repository


class RepositoryAnalytics:
    """Read-only analytics helpers over workflow and execution tables."""

    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def workflow_summary(self) -> Dict[str, Any]:
        workflows = self._repository.list_workflows(limit=500)
        return {
            "total_workflows": len(workflows),
            "average_nodes": (
                sum(len(item["definition"]["nodes"]) for item in workflows) / len(workflows)
                if workflows
                else 0.0
            ),
            "names": [item["name"] for item in workflows[:20]],
        }

    def execution_summary(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        executions = self._repository.list_executions(workflow_id=workflow_id)
        statuses = Counter(item["status"] for item in executions if item)
        return {
            "total_executions": len(executions),
            "by_status": dict(statuses),
            "recent": [
                {"id": item["id"], "status": item["status"], "workflow_id": item["workflow_id"]}
                for item in executions[:10]
                if item
            ],
        }

    def plugin_usage_from_logs(self, execution_id: str, workflow: Dict[str, Any]) -> Dict[str, int]:
        logs = self._repository.list_execution_logs(execution_id)
        plugin_by_node = {node["id"]: node["plugin"] for node in workflow["definition"]["nodes"]}
        counter: Counter[str] = Counter()
        for log in logs:
            plugin = plugin_by_node.get(log["node_id"], "unknown")
            counter[plugin] += 1
        return dict(counter)

    def metrics_summary(self, execution_id: str) -> Dict[str, Any]:
        metrics = self._repository.list_metrics(execution_id)
        if not metrics:
            return {"count": 0, "total_duration_ms": 0, "average_duration_ms": 0.0}
        total = sum(item["duration_ms"] for item in metrics)
        return {
            "count": len(metrics),
            "total_duration_ms": total,
            "average_duration_ms": total / len(metrics),
            "max_duration_ms": max(item["duration_ms"] for item in metrics),
        }
