import json
from pathlib import Path

import pytest

from cli.commands import load_workflow, validate_workflow


FIXTURE_DIR = Path(__file__).resolve().parent / "data" / "workflows"


@pytest.mark.parametrize("path", sorted(FIXTURE_DIR.glob("*.json")))
def test_fixture_workflows_validate(path, registry):
    workflow = load_workflow(path)
    errors = validate_workflow(workflow, registry)
    assert errors == [], f"{path.name}: {errors}"


@pytest.mark.parametrize("path", sorted(FIXTURE_DIR.glob("*.json")))
@pytest.mark.asyncio
async def test_fixture_workflows_execute(path, engine, repository):
    from workflows.service import WorkflowService

    workflow = load_workflow(path)
    service = WorkflowService(repository)
    stored = service.create_workflow(workflow)
    result = await engine.run_workflow(stored.id, {}, async_mode=False)
    assert result.status.value == "succeeded", path.name
