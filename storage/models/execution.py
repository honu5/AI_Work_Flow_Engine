from __future__ import annotations

from datetime import datetime
import json

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from storage.models.base import Base


class ExecutionRecord(Base):
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[str] = mapped_column(String(64), default=lambda: datetime.utcnow().isoformat())
    finished_at: Mapped[str] = mapped_column(String(64), nullable=True)
    result_json: Mapped[str] = mapped_column(Text, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)


class ExecutionLogRecord(Base):
    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(String(64), ForeignKey("executions.id"))
    node_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    output_json: Mapped[str] = mapped_column(Text, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[str] = mapped_column(String(64), default=lambda: datetime.utcnow().isoformat())
    finished_at: Mapped[str] = mapped_column(String(64), nullable=True)

    def to_dict(self) -> dict:
        output = None
        if self.output_json is not None:
            output = json.loads(self.output_json)
        return {
            "execution_id": self.execution_id,
            "node_id": self.node_id,
            "status": self.status,
            "output": output,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
