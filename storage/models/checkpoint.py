from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from storage.models.base import Base


class ExecutionCheckpointRecord(Base):
    __tablename__ = "execution_checkpoints"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    execution_id: Mapped[str] = mapped_column(String(64), ForeignKey("executions.id"), index=True)
    node_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    outputs_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(64), default=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "node_id": self.node_id,
            "status": self.status,
            "outputs": json.loads(self.outputs_json),
            "created_at": self.created_at,
        }
