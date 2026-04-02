from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.service import WorkflowService


def test_workflow_versions(repository):
    service = WorkflowService(repository)
    workflow = service.create_workflow(
        WorkflowCreate(name="versions", nodes=[WorkflowNode(id="n1", plugin="echo")])
    )

    versions = repository.list_workflow_versions(workflow.id)
    assert versions
    assert versions[0]["version"] == 1
