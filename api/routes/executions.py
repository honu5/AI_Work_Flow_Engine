from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_repository
from execution.checkpoint import CheckpointManager
from execution.trace import build_trace_from_execution
from storage.repository import Repository

router = APIRouter()


@router.get("/{execution_id}")
async def get_execution(execution_id: str, repository: Repository = Depends(get_repository)):
    execution = repository.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/")
async def list_executions(
    workflow_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    repository: Repository = Depends(get_repository),
):
    return repository.list_executions(workflow_id=workflow_id, status=status)


@router.get("/{execution_id}/logs")
async def list_execution_logs(execution_id: str, repository: Repository = Depends(get_repository)):
    logs = repository.list_execution_logs(execution_id)
    if not logs:
        raise HTTPException(status_code=404, detail="Execution logs not found")
    return logs


@router.get("/{execution_id}/trace")
async def get_execution_trace(execution_id: str, repository: Repository = Depends(get_repository)):
    execution = repository.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    workflow = repository.get_workflow(execution["workflow_id"])
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return build_trace_from_execution(execution, workflow).to_dict()


@router.get("/{execution_id}/checkpoints")
async def list_execution_checkpoints(execution_id: str, repository: Repository = Depends(get_repository)):
    execution = repository.get_execution(execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    manager = CheckpointManager(repository)
    return manager.list_for_execution(execution_id)
