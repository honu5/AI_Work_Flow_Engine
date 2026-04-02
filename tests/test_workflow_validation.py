import pytest

from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService
from utils.errors import WorkflowValidationError


def test_workflow_validation(repository):
    service = WorkflowService(repository)
    with pytest.raises(WorkflowValidationError):
        service.create_workflow(
            WorkflowCreate(
                name="bad-flow",
                nodes=[
                    WorkflowNode(id="n1", plugin="echo", depends_on=["n2"]),
                    WorkflowNode(id="n2", plugin="echo", depends_on=["n1"]),
                ],
            )
        )
