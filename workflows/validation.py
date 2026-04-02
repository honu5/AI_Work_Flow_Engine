from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from plugins.registry import PluginRegistry
from utils.errors import WorkflowValidationError
from workflows.graph import GraphNode, WorkflowGraph
from workflows.schema import WorkflowNode


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]


class WorkflowValidator:
    def __init__(self, registry: Optional[PluginRegistry] = None) -> None:
        self._registry = registry

    def validate(self, nodes: Iterable[WorkflowNode]) -> ValidationResult:
        errors: List[str] = []
        node_list = list(nodes)
        ids = [node.id for node in node_list]
        if len(ids) != len(set(ids)):
            errors.append("Duplicate node ids in workflow")

        known = set(ids)
        for node in node_list:
            for dep in node.depends_on:
                if dep not in known:
                    errors.append(f"Unknown dependency {dep} in workflow")

        graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in node_list])
        if graph.has_cycle():
            errors.append("Workflow has circular dependencies")

        if self._registry is not None:
            for node in node_list:
                try:
                    self._registry.get(node.plugin)
                except Exception:
                    errors.append(f"Plugin {node.plugin} not registered")
                    continue
                if node.requires:
                    details = self._registry.get_details(node.plugin)
                    capabilities = set(details.get("capabilities", []))
                    for requirement in node.requires:
                        if requirement not in capabilities:
                            errors.append(
                                f"Plugin {node.plugin} missing capability {requirement}"
                            )

        return ValidationResult(valid=not errors, errors=errors)

    def require_valid(self, nodes: Iterable[WorkflowNode]) -> None:
        result = self.validate(nodes)
        if not result.valid:
            raise WorkflowValidationError("; ".join(result.errors))
