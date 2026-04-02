import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


class CounterPlugin(Plugin):
    name = "counter"
    version = "1.0.0"
    description = "Counts invocations."

    def __init__(self):
        self.count = 0

    async def run(self, payload):
        self.count += 1
        return {"count": self.count}


@pytest.mark.asyncio
async def test_cache_reuse(engine, repository):
    registry = PluginRegistry(repository)
    counter = CounterPlugin()
    registry.register(counter)
    engine._registry = registry

    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="cache-flow",
            nodes=[WorkflowNode(id="n1", plugin="counter")],
        )
    )

    result_one = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    result_two = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)

    assert result_one.output["nodes"]["n1"]["count"] == 1
    assert result_two.output["nodes"]["n1"]["count"] == 1
