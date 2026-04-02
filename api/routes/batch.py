from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_engine, get_repository
from workflows.schema import WorkflowCreate
from workflows.service import WorkflowService

router = APIRouter()


class BatchExecuteRequest(BaseModel):
    workflows: List[WorkflowCreate] = Field(min_length=1, max_length=20)
    checkpoint: bool = False


@router.post("/execute")
async def batch_execute(
    payload: BatchExecuteRequest,
    engine=Depends(get_engine),
    repository=Depends(get_repository),
):
    service = WorkflowService(repository)
    results = []
    for definition in payload.workflows:
        workflow = service.create_workflow(definition)
        result = await engine.run_workflow(
            workflow.id,
            {},
            async_mode=False,
            checkpoint=payload.checkpoint,
        )
        results.append(
            {
                "workflow_id": workflow.id,
                "workflow_name": definition.name,
                "execution_id": result.execution_id,
                "status": result.status.value,
            }
        )
    failures = [item for item in results if item["status"] != "succeeded"]
    if failures and len(failures) == len(results):
        raise HTTPException(status_code=500, detail={"results": results})
    return {"results": results, "failed": len(failures)}
