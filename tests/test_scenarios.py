import pytest

from workflows.scenarios import list_scenario_builders
from workflows.scenarios.builders import build_scenario
from workflows.validation import WorkflowValidator
from workflows.workflow_compiler import compile_workflow


def test_scenario_registry_lists_builders():
    names = list_scenario_builders()
    assert "document_ingest" in names
    assert len(names) >= 10


@pytest.mark.parametrize("name", list_scenario_builders())
def test_each_scenario_compiles(name, registry):
    workflow = build_scenario(name)
    compiled = compile_workflow(workflow, registry=registry)
    assert compiled.valid, compiled.diagnostics
    validation = WorkflowValidator(registry).validate(workflow.nodes)
    assert validation.valid, validation.errors


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["document_ingest", "customer_feedback", "compliance_review"])
async def test_scenario_executes(name, engine, repository):
    from workflows.service import WorkflowService

    workflow = build_scenario(name)
    service = WorkflowService(repository)
    stored = service.create_workflow(workflow)
    result = await engine.run_workflow(stored.id, {}, async_mode=False)
    assert result.status.value == "succeeded"
