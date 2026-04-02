import json
from pathlib import Path

from cli.commands import export_workflow, import_workflow, load_workflow, validate_workflow
from workflows.schema import WorkflowCreate, WorkflowNode


def test_cli_import_export(repository, tmp_path: Path):
    payload = WorkflowCreate(name="cli", nodes=[WorkflowNode(id="n1", plugin="echo")])
    workflow_id = import_workflow(repository, payload)

    output_path = tmp_path / "workflow.json"
    export_workflow(repository, workflow_id, output_path)
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["name"] == "cli"


def test_cli_validate():
    payload = WorkflowCreate(name="cli", nodes=[WorkflowNode(id="n1", plugin="echo")])
    errors = validate_workflow(payload)
    assert errors == []


def test_cli_load_workflow(tmp_path: Path):
    data = {"name": "cli", "nodes": [{"id": "n1", "plugin": "echo"}]}
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    payload = load_workflow(path)
    assert payload.name == "cli"
