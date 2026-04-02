"""End-to-end engine scenarios using built-in plugin packs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli.commands import import_workflow, load_workflow, validate_workflow
from workflows.recipes import (
    build_analysis_workflow,
    build_catalog,
    build_reporting_workflow,
    build_routing_workflow,
    build_text_pipeline_workflow,
    build_validation_workflow,
)
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


@pytest.mark.asyncio
async def test_text_pipeline_recipe(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(build_text_pipeline_workflow())
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    nodes = result.output["nodes"]
    assert nodes["normalize"]["text"] == "example"
    assert "tokens" in nodes["tokenize"]
    assert nodes["count"]["words"] >= 1


@pytest.mark.asyncio
async def test_analysis_recipe(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(build_analysis_workflow())
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    nodes = result.output["nodes"]
    assert nodes["density"]["total_words"] >= 3
    assert nodes["profile"]["average"] == 3.0


@pytest.mark.asyncio
async def test_validation_recipe_marks_missing_keys(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(build_validation_workflow())
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.output["nodes"]["required"]["missing"] == ["id"]


@pytest.mark.asyncio
async def test_reporting_recipe_groups_and_sorts(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(build_reporting_workflow())
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.output["nodes"]["sort"]["values"] == [1, 2, 3]


@pytest.mark.asyncio
async def test_routing_recipe_join_output(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(build_routing_workflow())
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.output["nodes"]["format"]["text"] == "route::workflow"


@pytest.mark.asyncio
async def test_catalog_recipes_are_valid(registry):
    for recipe in build_catalog():
        errors = validate_workflow(recipe, registry)
        assert errors == [], f"{recipe.name}: {errors}"


@pytest.mark.asyncio
async def test_example_fixture_import_and_run(engine, repository, registry, tmp_path):
    fixture = Path(__file__).resolve().parents[1] / "examples" / "text_pipeline.json"
    payload = load_workflow(fixture)
    assert validate_workflow(payload, registry) == []
    workflow_id = import_workflow(repository, payload)
    result = await engine.run_workflow(workflow_id, {}, async_mode=False)
    assert result.output["nodes"]["count"]["words"] >= 1


def test_all_catalog_entries_have_unique_names():
    names = [w.name for w in build_catalog()]
    assert len(names) == len(set(names))


@pytest.mark.asyncio
async def test_sequential_join_after_normalize(engine, repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(
            name="sequential-join",
            nodes=[
                WorkflowNode(
                    id="normalize",
                    plugin="text.normalize",
                    input={"text": "  A  ", "lowercase": True, "strip": True},
                ),
                WorkflowNode(
                    id="join",
                    plugin="format.join",
                    input={"values": ["prefix", "suffix"], "separator": "-"},
                    depends_on=["normalize"],
                ),
            ],
        )
    )
    result = await engine.run_workflow(workflow.id, {}, async_mode=False)
    assert result.output["nodes"]["normalize"]["text"] == "a"
    assert result.output["nodes"]["join"]["text"] == "prefix-suffix"


def test_examples_directory_fixtures_parse():
    examples = Path(__file__).resolve().parents[1] / "examples"
    for path in sorted(examples.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        wf = WorkflowCreate(**data)
        assert wf.nodes
