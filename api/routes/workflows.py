from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_engine, get_repository
from workflows.schema import ExecutionRequest, WorkflowCreate, WorkflowResponse
from workflows.service import WorkflowService

router = APIRouter()


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(payload: WorkflowCreate, repository=Depends(get_repository)):
    service = WorkflowService(repository)
    workflow = service.create_workflow(payload)
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, repository=Depends(get_repository)):
    service = WorkflowService(repository)
    workflow = service.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.get("/")
async def list_workflows(
    name: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    repository=Depends(get_repository),
):
    return repository.list_workflows(name_contains=name, offset=offset, limit=limit)


@router.get("/{workflow_id}/versions")
async def list_workflow_versions(workflow_id: str, repository=Depends(get_repository)):
    return repository.list_workflow_versions(workflow_id)


@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    payload: ExecutionRequest,
    engine=Depends(get_engine),
):
    if payload.workflow_id and payload.workflow_id != workflow_id:
        raise HTTPException(status_code=400, detail="Workflow id mismatch")
    result = await engine.run_workflow(workflow_id, payload.input, payload.async_mode)
    return result
