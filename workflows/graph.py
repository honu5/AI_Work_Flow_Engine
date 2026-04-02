from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    depends_on: List[str]


class WorkflowGraph:
    def __init__(self, nodes: Iterable[GraphNode]) -> None:
        self._nodes = {node.node_id: node for node in nodes}
        self._edges: Dict[str, Set[str]] = defaultdict(set)
        for node in nodes:
            for dep in node.depends_on:
                self._edges[node.node_id].add(dep)

    def node_ids(self) -> List[str]:
        return list(self._nodes.keys())

    def dependencies(self, node_id: str) -> Set[str]:
        return set(self._edges.get(node_id, set()))

    def reverse_dependencies(self, node_id: str) -> Set[str]:
        dependents = set()
        for candidate, deps in self._edges.items():
            if node_id in deps:
                dependents.add(candidate)
        return dependents

    def has_cycle(self) -> bool:
        return len(self.topological_sort()) != len(self._nodes)

    def topological_sort(self) -> List[str]:
        deps = {node_id: set(self.dependencies(node_id)) for node_id in self._nodes}
        ready = deque([node_id for node_id, edges in deps.items() if not edges])
        order: List[str] = []

        while ready:
            current = ready.popleft()
            order.append(current)
            for node_id, edges in deps.items():
                if current in edges:
                    edges.remove(current)
                    if not edges:
                        if node_id not in order and node_id not in ready:
                            ready.append(node_id)
        return order

    def levels(self) -> List[List[str]]:
        deps = {node_id: set(self.dependencies(node_id)) for node_id in self._nodes}
        remaining = set(self._nodes.keys())
        levels: List[List[str]] = []

        while remaining:
            level = [node_id for node_id in remaining if not deps[node_id]]
            if not level:
                return []
            levels.append(level)
            for node_id in level:
                remaining.remove(node_id)
                for downstream in deps:
                    deps[downstream].discard(node_id)
        return levels

    def critical_path_length(self) -> int:
        path = self.critical_path()
        return max(len(path) - 1, 0)

    def critical_path(self) -> List[str]:
        order = self.topological_sort()
        if not order:
            return []
        distances: Dict[str, int] = {node_id: 0 for node_id in order}
        predecessors: Dict[str, str | None] = {node_id: None for node_id in order}
        for node_id in order:
            for dep in self.dependencies(node_id):
                candidate = distances[dep] + 1
                if candidate > distances[node_id]:
                    distances[node_id] = candidate
                    predecessors[node_id] = dep
        if not distances:
            return []
        end = max(distances, key=distances.get)
        path: List[str] = []
        current: str | None = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        return path
