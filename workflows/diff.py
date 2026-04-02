from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from workflows.schema import WorkflowCreate, WorkflowNode


@dataclass
class NodeChange:
    node_id: str
    change_type: str
    before: Dict[str, object] | None = None
    after: Dict[str, object] | None = None


@dataclass
class WorkflowDiff:
    added_nodes: List[str] = field(default_factory=list)
    removed_nodes: List[str] = field(default_factory=list)
    changed_nodes: List[NodeChange] = field(default_factory=list)
    renamed: bool = False
    before_name: str = ""
    after_name: str = ""

    def has_changes(self) -> bool:
        return bool(self.added_nodes or self.removed_nodes or self.changed_nodes or self.renamed)

    def summary(self) -> Dict[str, object]:
        return {
            "renamed": self.renamed,
            "before_name": self.before_name,
            "after_name": self.after_name,
            "added": self.added_nodes,
            "removed": self.removed_nodes,
            "changed": [
                {"node_id": change.node_id, "type": change.change_type}
                for change in self.changed_nodes
            ],
        }


def diff_workflows(before: WorkflowCreate, after: WorkflowCreate) -> WorkflowDiff:
    result = WorkflowDiff(
        renamed=before.name != after.name,
        before_name=before.name,
        after_name=after.name,
    )
    before_map = {node.id: node for node in before.nodes}
    after_map = {node.id: node for node in after.nodes}
    before_ids = set(before_map)
    after_ids = set(after_map)

    result.added_nodes = sorted(after_ids - before_ids)
    result.removed_nodes = sorted(before_ids - after_ids)

    for node_id in sorted(before_ids & after_ids):
        left = before_map[node_id]
        right = after_map[node_id]
        if left.model_dump() != right.model_dump():
            result.changed_nodes.append(
                NodeChange(
                    node_id=node_id,
                    change_type="modified",
                    before=left.model_dump(),
                    after=right.model_dump(),
                )
            )
    return result


def patch_workflow(base: WorkflowCreate, diff: WorkflowDiff) -> WorkflowCreate:
    nodes: Dict[str, WorkflowNode] = {node.id: node for node in base.nodes}
    for node_id in diff.removed_nodes:
        nodes.pop(node_id, None)
    for change in diff.changed_nodes:
        if change.after is not None:
            nodes[change.node_id] = WorkflowNode(**change.after)
    return WorkflowCreate(name=diff.after_name or base.name, nodes=list(nodes.values()))
