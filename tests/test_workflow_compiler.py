from workflows.recipes import build_text_pipeline_workflow
from workflows.workflow_compiler import compile_workflow


def test_compile_workflow_reports_stages(registry):
    workflow = build_text_pipeline_workflow()
    compiled = compile_workflow(workflow, registry=registry)
    assert compiled.valid
    assert compiled.stages
    assert compiled.critical_path


def test_compile_invalid_plugin_reports_error(registry):
    from workflows.schema import WorkflowCreate, WorkflowNode

    workflow = WorkflowCreate(
        name="bad",
        nodes=[WorkflowNode(id="n1", plugin="missing.plugin", input={})],
    )
    compiled = compile_workflow(workflow, registry=registry)
    assert not compiled.valid
    assert any("not registered" in diag.message for diag in compiled.diagnostics)
