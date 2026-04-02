from pathlib import Path

import pytest

from workflows.catalog.loader import load_catalog
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_execute_incident_triage_catalog_workflow(engine, repository):
    directory = Path(__file__).resolve().parents[2] / "workflows" / "catalog"
    template = next(item for item in load_catalog(directory) if item.name == "incident_triage")
    service = WorkflowService(repository)
    workflow = service.create_workflow(template)
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.status.value == "succeeded"
    assert "report" in result.output["nodes"]


@pytest.mark.asyncio
async def test_execute_user_onboarding_catalog_workflow(engine, repository):
    directory = Path(__file__).resolve().parents[2] / "workflows" / "catalog"
    template = next(item for item in load_catalog(directory) if item.name == "user_onboarding")
    service = WorkflowService(repository)
    workflow = service.create_workflow(template)
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.status.value == "succeeded"
