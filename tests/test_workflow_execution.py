import pytest

from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_simple_workflow_execution(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="adder",
            nodes=[
                WorkflowNode(id="n1", plugin="add_numbers", input={"a": 2, "b": 3}),
            ],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    assert result.status.value == "succeeded"
    assert result.output["nodes"]["n1"]["sum"] == 5
