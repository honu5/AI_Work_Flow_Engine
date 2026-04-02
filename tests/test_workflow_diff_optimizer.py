from workflows.diff import diff_workflows
from workflows.optimizer import optimize_workflow, prune_unreachable_nodes
from workflows.schema import WorkflowCreate, WorkflowNode


def test_diff_detects_added_node():
    before = WorkflowCreate(name="flow", nodes=[WorkflowNode(id="a", plugin="echo", input={})])
    after = WorkflowCreate(
        name="flow",
        nodes=[
            WorkflowNode(id="a", plugin="echo", input={}),
            WorkflowNode(id="b", plugin="echo", input={}, depends_on=["a"]),
        ],
    )
    result = diff_workflows(before, after)
    assert result.added_nodes == ["b"]


def test_optimizer_keeps_connected_dag():
    workflow = WorkflowCreate(
        name="flow",
        nodes=[
            WorkflowNode(id="root", plugin="echo", input={"message": "start"}),
            WorkflowNode(id="child", plugin="echo", input={"message": "next"}, depends_on=["root"]),
        ],
    )
    pruned = prune_unreachable_nodes(workflow)
    assert len(pruned.nodes) == 2
    optimized = optimize_workflow(workflow)
    assert [node.id for node in optimized.nodes] == ["root", "child"]
