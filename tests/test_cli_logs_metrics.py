import pytest

from cli.commands import export_logs, export_metrics
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_cli_logs_metrics(repository, engine):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(name="cli", nodes=[WorkflowNode(id="n1", plugin="echo")])
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    logs = export_logs(repository, result.execution_id)
    metrics = export_metrics(repository, result.execution_id)

    assert logs
    assert metrics
