import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


class ProducePlugin(Plugin):
    name = "produce"
    version = "1.0.0"
    description = "Produces a base value."

    async def run(self, payload):
        return {"value": 5}


class MultiplyPlugin(Plugin):
    name = "multiply"
    version = "1.0.0"
    description = "Multiplies prior output by a factor."

    async def run(self, payload):
        base = payload["outputs"]["n1"]["value"]
        factor = payload.get("factor", 2)
        return {"value": base * factor}


class SummarizePlugin(Plugin):
    name = "summarize"
    version = "1.0.0"
    description = "Combines values into a summary payload."

    async def run(self, payload):
        original = payload["outputs"]["n1"]["value"]
        derived = payload["outputs"]["n2"]["value"]
        return {"summary": f"{original}:{derived}"}


@pytest.mark.asyncio
async def test_multi_node_dag_execution(engine, repository, registry):
    custom_registry = PluginRegistry(repository)
    custom_registry.register(ProducePlugin())
    custom_registry.register(MultiplyPlugin())
    custom_registry.register(SummarizePlugin())
    engine._registry = custom_registry

    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="dag-flow",
            nodes=[
                WorkflowNode(id="n1", plugin="produce"),
                WorkflowNode(
                    id="n2",
                    plugin="multiply",
                    input={"factor": 3},
                    depends_on=["n1"],
                ),
                WorkflowNode(
                    id="n3",
                    plugin="summarize",
                    depends_on=["n1", "n2"],
                ),
            ],
        )
    )

    result = await engine.run_workflow(workflow.id, input_payload={}, async_mode=False)

    assert result.output["nodes"]["n1"]["value"] == 5
    assert result.output["nodes"]["n2"]["value"] == 15
    assert result.output["nodes"]["n3"]["summary"] == "5:15"
