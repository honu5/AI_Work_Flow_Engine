from workflows.graph import GraphNode, WorkflowGraph


def test_graph_levels():
    graph = WorkflowGraph(
        [
            GraphNode("n1", []),
            GraphNode("n2", ["n1"]),
            GraphNode("n3", ["n1"]),
            GraphNode("n4", ["n2", "n3"]),
        ]
    )
    levels = graph.levels()
    assert levels[0] == ["n1"]
    assert set(levels[1]) == {"n2", "n3"}
    assert levels[2] == ["n4"]


def test_critical_path_length():
    graph = WorkflowGraph(
        [
            GraphNode("n1", []),
            GraphNode("n2", ["n1"]),
            GraphNode("n3", ["n2"]),
        ]
    )
    assert graph.critical_path_length() == 2
