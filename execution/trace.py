from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TraceEvent:
    node_id: str
    plugin: str
    status: str
    duration_ms: float = 0.0
    attempts: int = 1
    error: Optional[str] = None


@dataclass
class ExecutionTrace:
    execution_id: str
    workflow_id: str
    events: List[TraceEvent] = field(default_factory=list)

    def record(
        self,
        node_id: str,
        plugin: str,
        status: str,
        duration_ms: float = 0.0,
        attempts: int = 1,
        error: Optional[str] = None,
    ) -> None:
        self.events.append(
            TraceEvent(
                node_id=node_id,
                plugin=plugin,
                status=status,
                duration_ms=duration_ms,
                attempts=attempts,
                error=error,
            )
        )

    def failed_nodes(self) -> List[TraceEvent]:
        return [event for event in self.events if event.status == "failed"]

    def total_duration_ms(self) -> float:
        return sum(event.duration_ms for event in self.events)

    def plugins_used(self) -> List[str]:
        return sorted({event.plugin for event in self.events})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "total_duration_ms": self.total_duration_ms(),
            "plugins": self.plugins_used(),
            "events": [event.__dict__ for event in self.events],
        }


def build_trace_from_execution(execution: Dict[str, Any], workflow: Dict[str, Any]) -> ExecutionTrace:
    trace = ExecutionTrace(
        execution_id=execution["id"],
        workflow_id=execution["workflow_id"],
    )
    node_plugins = {node["id"]: node["plugin"] for node in workflow["definition"]["nodes"]}
    for log in execution.get("logs", []):
        trace.record(
            node_id=log["node_id"],
            plugin=node_plugins.get(log["node_id"], "unknown"),
            status=log["status"],
            error=log.get("error"),
        )
    return trace
