from workflows.graph import GraphNode, WorkflowGraph


def test_critical_path_nodes():
    graph = WorkflowGraph(
        [
            GraphNode("n1", []),
            GraphNode("n2", ["n1"]),
            GraphNode("n3", ["n2"]),
        ]
    )
    assert graph.critical_path() == ["n1", "n2", "n3"]
    assert graph.critical_path_length() == 2
