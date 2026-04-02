import json
from pathlib import Path

import pytest

from cli.batch import run_catalog_subset_sync
from cli.inspect import (
    catalog_summary,
    describe_plugin,
    describe_workflow,
    format_json,
    list_registered_plugins,
)
from execution.checkpoint import CheckpointManager
from execution.trace import build_trace_from_execution
from workflows.dsl import compile_dsl
from workflows.expressions.evaluator import Evaluator
from workflows.expressions.errors import ExpressionError
from workflows.expressions.parser import ExpressionParser
from workflows.expressions.stdlib import build_default_functions
from workflows.recipes import build_analysis_workflow, build_text_pipeline_workflow
from workflows.service import WorkflowService


def _catalog_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "workflows" / "catalog"


def test_compile_dsl_multiple_shapes():
    source = """
    workflow parse_demo {
      node first plugin echo {
        message: "hello"
      }
      node second plugin add_numbers {
        a: 4
        b: 9
      } depends first
      node third plugin validate.range {
        value: 12
        minimum: 1
        maximum: 20
      } depends second
    }
    """
    workflow = compile_dsl(source)
    assert workflow.name == "parse_demo"
    assert [node.id for node in workflow.nodes] == ["first", "second", "third"]
    assert workflow.nodes[1].depends_on == ["first"]


def test_compile_dsl_invalid_raises():
    source = "workflow broken { node a plugin echo { message: \"x\" }"
    with pytest.raises(SyntaxError):
        compile_dsl(source)


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("avg(2, 4, 6, 8)", 5.0),
        ("clamp(11, 0, 10)", 10),
        ("between(7, 1, 8)", True),
        ("coalesce(0, 4, 5)", 0),
        ("pow(2, 5)", 32),
        ("ceil(2.2)", 3),
        ("floor(2.9)", 2),
        ("sqrt(16)", 4),
    ],
)
def test_expression_stdlib_matrix(expression, expected):
    parsed = ExpressionParser(expression).parse()
    result = Evaluator({}, build_default_functions()).evaluate(parsed)
    assert result == expected


def test_expression_unknown_identifier_and_function():
    with pytest.raises(ExpressionError):
        Evaluator({}, build_default_functions()).evaluate(ExpressionParser("x + 1").parse())
    with pytest.raises(ExpressionError):
        Evaluator({}, build_default_functions()).evaluate(ExpressionParser("unknown_fn(1)").parse())


def test_cli_inspect_helpers(registry):
    plugin = describe_plugin(registry, "echo")
    assert plugin["name"] == "echo"
    assert "description" in plugin

    plugins = list_registered_plugins(registry)
    assert len(plugins) > 20

    workflow_description = describe_workflow(build_text_pipeline_workflow(), registry)
    assert workflow_description["node_count"] >= 4
    assert workflow_description["valid"] is True

    payload = format_json({"a": 1, "b": 2})
    assert json.loads(payload) == {"a": 1, "b": 2}


def test_catalog_summary_contains_expected_templates():
    summary = catalog_summary(_catalog_dir())
    names = {item["name"] for item in summary}
    assert "incident_triage" in names
    assert len(names) >= 15


@pytest.mark.asyncio
async def test_checkpoint_manager_snapshot(repository, engine):
    service = WorkflowService(repository)
    created = service.create_workflow(build_text_pipeline_workflow())
    run = await engine.run_workflow(created.id, {}, async_mode=False, checkpoint=True)

    manager = CheckpointManager(repository)
    latest = manager.latest_for_execution(run.execution_id)
    assert latest is not None
    assert latest["execution_id"] == run.execution_id
    assert manager.outputs_snapshot(run.execution_id)


@pytest.mark.asyncio
async def test_execution_trace_builder(repository, engine):
    service = WorkflowService(repository)
    created = service.create_workflow(build_analysis_workflow())
    run = await engine.run_workflow(created.id, {}, async_mode=False)

    execution = repository.get_execution(run.execution_id)
    workflow = repository.get_workflow(created.id)
    trace = build_trace_from_execution(execution, workflow)
    payload = trace.to_dict()
    assert payload["execution_id"] == run.execution_id
    assert payload["plugins"]
    assert isinstance(payload["events"], list)


def test_cli_batch_runner_smoke(repository, engine):
    rows = run_catalog_subset_sync(engine, repository, _catalog_dir(), limit=2)
    assert len(rows) == 2
    assert all(row["status"] in {"succeeded", "failed"} for row in rows)
