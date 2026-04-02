import pytest

from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_async_execution(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="async-flow",
            nodes=[WorkflowNode(id="sleep", plugin="sleep", input={"seconds": 0.01})],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=True)
    assert result.status.value == "succeeded"
    assert result.output["nodes"]["sleep"]["slept"] == 0.01
