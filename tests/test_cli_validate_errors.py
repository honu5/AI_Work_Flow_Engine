from workflows.schema import WorkflowCreate, WorkflowNode
from cli.commands import validate_workflow


def test_cli_validate_reports_errors():
    payload = WorkflowCreate(
        name="cli",
        nodes=[
            WorkflowNode(id="n1", plugin="echo", depends_on=["missing"]),
        ],
    )
    errors = validate_workflow(payload)
    assert errors
