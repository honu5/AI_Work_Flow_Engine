from workflows.linter import WorkflowLinter
from workflows.schema import WorkflowCreate, WorkflowNode


def test_linter_detects_duplicate_ids():
    workflow = WorkflowCreate(
        name="dup",
        nodes=[
            WorkflowNode(id="n1", plugin="echo", input={"message": "a"}),
            WorkflowNode(id="n1", plugin="echo", input={"message": "b"}),
        ],
    )
    report = WorkflowLinter().lint(workflow.nodes)
    assert not report.ok()
    assert any(issue.rule == "duplicate_id" for issue in report.issues)


def test_linter_detects_unknown_dependency():
    workflow = WorkflowCreate(
        name="bad",
        nodes=[WorkflowNode(id="n1", plugin="echo", input={}, depends_on=["missing"])],
    )
    report = WorkflowLinter().lint(workflow.nodes)
    assert not report.ok()
