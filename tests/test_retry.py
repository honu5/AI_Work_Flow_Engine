import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


class FlakyPlugin(Plugin):
    name = "flaky"
    version = "1.0.0"
    description = "Fails once, then succeeds."

    def __init__(self):
        self.calls = 0

    async def run(self, payload):
        self.calls += 1
        if self.calls == 1:
            raise ValueError("temporary failure")
        return {"ok": True}


@pytest.mark.asyncio
async def test_retry_behavior(engine, repository):
    registry = PluginRegistry(repository)
    flaky = FlakyPlugin()
    registry.register(flaky)
    engine._registry = registry

    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="retry-flow",
            nodes=[
                WorkflowNode(
                    id="n1",
                    plugin="flaky",
                    retry={"max_attempts": 2, "backoff_seconds": 0.0},
                )
            ],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    assert result.status.value == "succeeded"
    assert flaky.calls == 2
