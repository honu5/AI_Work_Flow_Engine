from __future__ import annotations

from typing import Optional

from storage.repository import Repository
from utils.ids import new_id
from workflows.schema import WorkflowCreate, WorkflowNode, WorkflowResponse
from workflows.validation import WorkflowValidator


class WorkflowService:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository
        self._validator = WorkflowValidator()

    def create_workflow(self, payload: WorkflowCreate) -> WorkflowResponse:
        self._validator.require_valid(payload.nodes)
        workflow_id = new_id("wf")
        self._repository.create_workflow(workflow_id, payload.name, payload.model_dump())
        self._repository.create_workflow_version(workflow_id, 1, payload.model_dump())
        return WorkflowResponse(id=workflow_id, name=payload.name, nodes=payload.nodes)

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowResponse]:
        record = self._repository.get_workflow(workflow_id)
        if record is None:
            return None
        data = record["definition"]
        return WorkflowResponse(id=record["id"], name=record["name"], nodes=[WorkflowNode(**node) for node in data["nodes"]])
