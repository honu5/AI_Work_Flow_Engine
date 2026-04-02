import pytest

from execution.checkpoint import CheckpointManager
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_checkpoint_saved_during_execution(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="checkpoint-flow",
            nodes=[
                WorkflowNode(id="n1", plugin="add_numbers", input={"a": 1, "b": 2}),
                WorkflowNode(id="n2", plugin="add_numbers", input={"a": 3, "b": 4}, depends_on=["n1"]),
            ],
        )
    )
    result = await engine.run_workflow(workflow.id, {}, async_mode=False, checkpoint=True)
    manager = CheckpointManager(repository)
    checkpoints = manager.list_for_execution(result.execution_id)
    assert len(checkpoints) == 2
    assert checkpoints[-1]["outputs"]["n2"]["sum"] == 7
