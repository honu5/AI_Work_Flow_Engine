from __future__ import annotations

from typing import List, Set

from workflows.graph import GraphNode, WorkflowGraph
from workflows.schema import WorkflowCreate, WorkflowNode


def prune_unreachable_nodes(workflow: WorkflowCreate) -> WorkflowCreate:
    if not workflow.nodes:
        return workflow
    graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in workflow.nodes])
    reachable = _reachable_ids(workflow.nodes)
    pruned = [node for node in workflow.nodes if node.id in reachable]
    return WorkflowCreate(name=workflow.name, nodes=pruned)


def merge_parallel_branches(workflow: WorkflowCreate) -> WorkflowCreate:
    """Collapse duplicate plugin chains that share identical dependencies and plugins."""
    groups: dict[tuple[str, tuple[str, ...]], List[WorkflowNode]] = {}
    for node in workflow.nodes:
        key = (node.plugin, tuple(sorted(node.depends_on)))
        groups.setdefault(key, []).append(node)
    merged_nodes: List[WorkflowNode] = []
    seen_ids: Set[str] = set()
    for node in workflow.nodes:
        key = (node.plugin, tuple(sorted(node.depends_on)))
        bucket = groups[key]
        if len(bucket) > 1 and node.id != bucket[0].id:
            continue
        if node.id in seen_ids:
            continue
        seen_ids.add(node.id)
        merged_nodes.append(node)
    return WorkflowCreate(name=workflow.name, nodes=merged_nodes)


def normalize_dependency_order(workflow: WorkflowCreate) -> WorkflowCreate:
    graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in workflow.nodes])
    order = graph.topological_sort()
    order_index = {node_id: index for index, node_id in enumerate(order)}
    sorted_nodes = sorted(workflow.nodes, key=lambda node: order_index.get(node.id, 0))
    return WorkflowCreate(name=workflow.name, nodes=sorted_nodes)


def optimize_workflow(workflow: WorkflowCreate) -> WorkflowCreate:
    optimized = prune_unreachable_nodes(workflow)
    optimized = merge_parallel_branches(optimized)
    return normalize_dependency_order(optimized)


def _reachable_ids(nodes: List[WorkflowNode]) -> Set[str]:
    roots = [node.id for node in nodes if not node.depends_on] or [nodes[0].id]
    reachable: Set[str] = set()
    stack = list(roots)
    while stack:
        current = stack.pop()
        if current in reachable:
            continue
        reachable.add(current)
        for node in nodes:
            if current in node.depends_on:
                stack.append(node.id)
    return reachable
