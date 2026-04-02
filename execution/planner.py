from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from workflows.graph import GraphNode, WorkflowGraph


@dataclass(frozen=True)
class PlanNode:
    node_id: str
    depends_on: List[str]


@dataclass(frozen=True)
class ExecutionPlan:
    stages: List[List[str]]

    def linear_order(self) -> List[str]:
        return [node_id for stage in self.stages for node_id in stage]


class ExecutionPlanner:
    def build(self, nodes: Iterable[Dict[str, object]]) -> ExecutionPlan:
        graph_nodes = [
            GraphNode(node_id=node["id"], depends_on=list(node.get("depends_on") or []))
            for node in nodes
        ]
        graph = WorkflowGraph(graph_nodes)
        stages = graph.levels()
        if not stages:
            raise ValueError("Unable to build execution plan due to cyclic dependencies")
        return ExecutionPlan(stages=stages)
