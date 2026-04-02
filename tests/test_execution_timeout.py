import asyncio

import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


class SlowPlugin(Plugin):
    name = "slow"
    version = "1.0.0"
    description = "slow"

    async def run(self, payload):
        await asyncio.sleep(0.02)
        return {"ok": True}


@pytest.mark.asyncio
async def test_execution_timeout(engine, repository):
    registry = PluginRegistry(repository)
    registry.register(SlowPlugin())
    engine._registry = registry

    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="timeout",
            nodes=[
                WorkflowNode(id="n1", plugin="slow", timeout_seconds=0.001),
            ],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)
    assert result.status.value == "failed"
