from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import and_, select

from storage.models.execution import ExecutionRecord


def build_execution_filters(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
) -> List:
    filters = []
    if workflow_id:
        filters.append(ExecutionRecord.workflow_id == workflow_id)
    if status:
        filters.append(ExecutionRecord.status == status)
    return filters
