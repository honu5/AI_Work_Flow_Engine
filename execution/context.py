from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class ExecutionMetric:
    node_id: str
    duration_ms: float
    attempts: int


@dataclass
class ExecutionContext:
    execution_id: str
    workflow_id: str
    input_payload: Dict[str, Any]
    async_mode: bool
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metrics: List[ExecutionMetric] = field(default_factory=list)

    def record_metric(self, metric: ExecutionMetric) -> None:
        self.metrics.append(metric)
