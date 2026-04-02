from pathlib import Path

import pytest
from httpx import AsyncClient

from cli.doctor import run_doctor
from execution.simulator import WorkflowSimulator
from storage.analytics import RepositoryAnalytics
from storage.query import ExecutionQuery, WorkflowQuery
from workflows.diff import diff_workflows, patch_workflow
from workflows.linter import WorkflowLinter
from workflows.optimizer import merge_parallel_branches, normalize_dependency_order
from workflows.recipes import (
    build_analysis_workflow,
    build_reporting_workflow,
    build_text_pipeline_workflow,
    build_validation_workflow,
)
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


def _sample_workflow(name: str = "sample") -> WorkflowCreate:
    return WorkflowCreate(
        name=name,
        nodes=[
            WorkflowNode(id="a", plugin="echo", input={"message": "start"}),
            WorkflowNode(id="b", plugin="add_numbers", input={"a": 1, "b": 2}, depends_on=["a"]),
            WorkflowNode(id="c", plugin="format.join", input={"values": ["x", "y"], "separator": ":"}, depends_on=["b"]),
        ],
    )


@pytest.mark.parametrize(
    "workflow",
    [
        _sample_workflow("lint-1"),
        build_text_pipeline_workflow(),
        build_analysis_workflow(),
        build_reporting_workflow(),
        build_validation_workflow(),
    ],
)
def test_linter_on_real_workflows(workflow):
    report = WorkflowLinter().lint(workflow.nodes)
    assert report.error_count == 0


def test_linter_cycle_and_empty_plugin():
    workflow = WorkflowCreate(
        name="bad",
        nodes=[
            WorkflowNode(id="a", plugin="echo", input={}, depends_on=["b"]),
            WorkflowNode(id="b", plugin="", input={}, depends_on=["a"]),
        ],
    )
    report = WorkflowLinter().lint(workflow.nodes)
    assert report.error_count >= 2
    assert any(issue.rule == "cycle" for issue in report.issues)
    assert any(issue.rule == "empty_plugin" for issue in report.issues)


def test_workflow_diff_and_patch_roundtrip():
    before = _sample_workflow("flow-A")
    after = WorkflowCreate(
        name="flow-B",
        nodes=[
            WorkflowNode(id="a", plugin="echo", input={"message": "start"}),
            WorkflowNode(id="b", plugin="add_numbers", input={"a": 5, "b": 7}, depends_on=["a"]),
            WorkflowNode(id="d", plugin="echo", input={"message": "new"}, depends_on=["b"]),
        ],
    )
    wf_diff = diff_workflows(before, after)
    assert wf_diff.renamed is True
    assert wf_diff.added_nodes == ["d"]
    assert wf_diff.removed_nodes == ["c"]
    assert wf_diff.has_changes() is True

    patched = patch_workflow(before, wf_diff)
    assert patched.name == "flow-B"
    assert {node.id for node in patched.nodes} == {"a", "b", "d"}


def test_optimizer_merge_and_ordering():
    workflow = WorkflowCreate(
        name="opt",
        nodes=[
            WorkflowNode(id="start", plugin="echo", input={"message": "s"}),
            WorkflowNode(id="dup1", plugin="echo", input={"message": "x"}, depends_on=["start"]),
            WorkflowNode(id="dup2", plugin="echo", input={"message": "y"}, depends_on=["start"]),
            WorkflowNode(id="end", plugin="format.join", input={"values": ["a", "b"], "separator": ","}, depends_on=["dup1"]),
        ],
    )
    merged = merge_parallel_branches(workflow)
    assert len(merged.nodes) < len(workflow.nodes)

    ordered = normalize_dependency_order(merged)
    assert ordered.nodes[0].id == "start"


def test_simulator_profiles_and_dict_output(registry):
    simulator = WorkflowSimulator(registry)
    result = simulator.simulate(_sample_workflow("sim"))
    payload = result.to_dict()
    assert payload["workflow_name"] == "sim"
    assert payload["valid"] is True
    assert payload["estimated_total_ms"] > 0
    assert len(payload["nodes"]) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "builder",
    [
        build_text_pipeline_workflow,
        build_analysis_workflow,
        build_reporting_workflow,
    ],
)
async def test_repository_analytics_summaries(repository, engine, builder):
    service = WorkflowService(repository)
    workflow = service.create_workflow(builder())
    await engine.run_workflow(workflow.id, {}, async_mode=False, checkpoint=True)

    analytics = RepositoryAnalytics(repository)
    wf_summary = analytics.workflow_summary()
    exec_summary = analytics.execution_summary(workflow_id=workflow.id)
    assert wf_summary["total_workflows"] >= 1
    assert exec_summary["total_executions"] >= 1

    execution_id = exec_summary["recent"][0]["id"]
    workflow_record = repository.get_workflow(workflow.id)
    usage = analytics.plugin_usage_from_logs(execution_id, workflow_record)
    assert isinstance(usage, dict)

    metric_summary = analytics.metrics_summary(execution_id)
    assert metric_summary["count"] >= 1


@pytest.mark.asyncio
async def test_query_builders(repository, engine):
    service = WorkflowService(repository)
    wf1 = service.create_workflow(_sample_workflow("query-alpha"))
    wf2 = service.create_workflow(_sample_workflow("query-beta"))
    await engine.run_workflow(wf1.id, {}, async_mode=False)
    await engine.run_workflow(wf2.id, {}, async_mode=False)

    workflows = WorkflowQuery().name_contains("query").limit(10).offset(0).execute()
    assert len(workflows) >= 2

    executions = ExecutionQuery().workflow_id(wf1.id).status("succeeded").limit(10).execute()
    assert executions
    assert all(item["workflow_id"] == wf1.id for item in executions)


def test_doctor_reports_expected_checks():
    project_root = Path(__file__).resolve().parents[1]
    report = run_doctor(project_root)
    names = {entry["name"] for entry in report["checks"]}
    assert {"catalog", "plugins", "linter"} <= names


@pytest.mark.asyncio
async def test_admin_and_batch_endpoints_extended(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        stats = await client.get("/admin/stats")
        assert stats.status_code == 200
        assert stats.json()["catalog_templates"] >= 1

        sim = await client.post(
            "/admin/simulate",
            json=_sample_workflow("remote-sim").model_dump(),
        )
        assert sim.status_code == 200
        assert sim.json()["valid"] is True

        batch_payload = {
            "workflows": [
                _sample_workflow("batch-1").model_dump(),
                _sample_workflow("batch-2").model_dump(),
            ],
            "checkpoint": True,
        }
        batch = await client.post("/batch/execute", json=batch_payload)
        assert batch.status_code == 200
        body = batch.json()
        assert len(body["results"]) == 2
        assert body["failed"] == 0


@pytest.mark.asyncio
async def test_catalog_detail_and_plugins_endpoints(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        templates = await client.get("/catalog/templates")
        assert templates.status_code == 200
        first_name = templates.json()[0]["name"]

        detail = await client.get(f"/catalog/templates/{first_name}")
        assert detail.status_code == 200
        assert "critical_path" in detail.json()

        plugins = await client.get("/plugins/")
        assert plugins.status_code == 200
        assert len(plugins.json()) > 20
