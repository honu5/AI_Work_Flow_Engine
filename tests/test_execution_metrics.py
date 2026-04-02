import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


class MetricsPlugin(Plugin):
    name = "metrics"
    version = "1.0.0"
    description = "Returns a fixed payload."

    async def run(self, payload):
        return {"ok": True}


@pytest.mark.asyncio
async def test_metrics_are_recorded(engine, repository):
    registry = PluginRegistry(repository)
    registry.register(MetricsPlugin())
    engine._registry = registry

    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(name="metrics", nodes=[WorkflowNode(id="n1", plugin="metrics")])
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    assert result.status.value == "succeeded"

    metrics = repository.list_metrics(result.execution_id)
    assert metrics
    assert metrics[0]["node_id"] == "n1"
