import pytest

from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_state_transitions(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="state-flow",
            nodes=[WorkflowNode(id="n1", plugin="echo")],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={"x": 1}, async_mode=False)
    execution = repository.get_execution(result.execution_id)
    assert execution["status"] == "succeeded"
    assert execution["result"]["nodes"]["n1"]["echo"]["input"]["x"] == 1
