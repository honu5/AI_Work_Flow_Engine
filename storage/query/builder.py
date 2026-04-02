from __future__ import annotations

from typing import Any, List, Optional

from sqlalchemy import select

from storage.db import get_session
from storage.models.execution import ExecutionRecord
from storage.models.workflow import WorkflowRecord


class WorkflowQuery:
    def __init__(self) -> None:
        self._name_contains: Optional[str] = None
        self._limit: int = 50
        self._offset: int = 0

    def name_contains(self, value: str) -> "WorkflowQuery":
        self._name_contains = value
        return self

    def limit(self, value: int) -> "WorkflowQuery":
        self._limit = value
        return self

    def offset(self, value: int) -> "WorkflowQuery":
        self._offset = value
        return self

    def execute(self) -> List[dict[str, Any]]:
        with get_session() as session:
            query = select(WorkflowRecord)
            if self._name_contains:
                query = query.where(WorkflowRecord.name.contains(self._name_contains))
            records = session.scalars(query.offset(self._offset).limit(self._limit)).all()
            return [{"id": record.id, "name": record.name} for record in records]


class ExecutionQuery:
    def __init__(self) -> None:
        self._workflow_id: Optional[str] = None
        self._status: Optional[str] = None
        self._limit: int = 100

    def workflow_id(self, value: str) -> "ExecutionQuery":
        self._workflow_id = value
        return self

    def status(self, value: str) -> "ExecutionQuery":
        self._status = value
        return self

    def limit(self, value: int) -> "ExecutionQuery":
        self._limit = value
        return self

    def execute(self) -> List[dict[str, Any]]:
        with get_session() as session:
            query = select(ExecutionRecord)
            if self._workflow_id:
                query = query.where(ExecutionRecord.workflow_id == self._workflow_id)
            if self._status:
                query = query.where(ExecutionRecord.status == self._status)
            records = session.scalars(query.limit(self._limit)).all()
            return [
                {
                    "id": record.id,
                    "workflow_id": record.workflow_id,
                    "status": record.status,
                    "started_at": record.started_at,
                    "finished_at": record.finished_at,
                }
                for record in records
            ]
