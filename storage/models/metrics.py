from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.models.base import Base


class ExecutionMetricRecord(Base):
    __tablename__ = "execution_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(64), ForeignKey("executions.id"))
    node_id: Mapped[str] = mapped_column(String(64))
    duration_ms: Mapped[int] = mapped_column(Integer)
    attempts: Mapped[int] = mapped_column(Integer)
    recorded_at: Mapped[str] = mapped_column(String(64), default=lambda: datetime.utcnow().isoformat())
