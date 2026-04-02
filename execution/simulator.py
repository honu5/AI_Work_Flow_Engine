from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from plugins.registry import PluginRegistry
from workflows.graph import GraphNode, WorkflowGraph
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.validation import WorkflowValidator
from workflows.workflow_compiler import compile_workflow


@dataclass
class SimulatedNode:
    node_id: str
    plugin: str
    stage: int
    depends_on: List[str]
    estimated_ms: float = 1.0
    cacheable: bool = False


@dataclass
class SimulationResult:
    workflow_name: str
    valid: bool
    stages: List[List[str]]
    critical_path: List[str]
    nodes: List[SimulatedNode] = field(default_factory=list)
    estimated_total_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_name": self.workflow_name,
            "valid": self.valid,
            "stages": self.stages,
            "critical_path": self.critical_path,
            "estimated_total_ms": self.estimated_total_ms,
            "errors": self.errors,
            "warnings": self.warnings,
            "nodes": [node.__dict__ for node in self.nodes],
        }


class WorkflowSimulator:
    """Dry-run planner that estimates execution shape without invoking plugins."""

    def __init__(self, registry: Optional[PluginRegistry] = None) -> None:
        self._registry = registry

    def simulate(self, workflow: WorkflowCreate) -> SimulationResult:
        compiled = compile_workflow(workflow, registry=self._registry)
        validation = WorkflowValidator(self._registry).validate(workflow.nodes)
        result = SimulationResult(
            workflow_name=workflow.name,
            valid=compiled.valid and validation.valid,
            stages=compiled.stages,
            critical_path=compiled.critical_path,
            errors=list(validation.errors),
            warnings=[diag.message for diag in compiled.diagnostics if diag.level == "warning"],
        )
        graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in workflow.nodes])
        stage_index = {node_id: idx for idx, level in enumerate(compiled.stages) for node_id in level}
        for node in workflow.nodes:
            estimated = self._estimate_node_cost(node)
            result.nodes.append(
                SimulatedNode(
                    node_id=node.id,
                    plugin=node.plugin,
                    stage=stage_index.get(node.id, 0),
                    depends_on=list(node.depends_on),
                    estimated_ms=estimated,
                    cacheable=bool(node.cache),
                )
            )
        if result.critical_path:
            result.estimated_total_ms = sum(
                next(sim.estimated_ms for sim in result.nodes if sim.node_id == node_id)
                for node_id in result.critical_path
            )
        else:
            result.estimated_total_ms = sum(node.estimated_ms for node in result.nodes)
        if graph.has_cycle():
            result.valid = False
            result.errors.append("Workflow graph contains a cycle")
        return result

    def _estimate_node_cost(self, node: WorkflowNode) -> float:
        base = 5.0
        if node.retry:
            base *= node.retry.get("limit", 1)
        if node.timeout_seconds:
            base = min(base, float(node.timeout_seconds) * 1000)
        if node.depends_on:
            base += 2.0 * len(node.depends_on)
        if node.plugin.startswith("analysis."):
            base += 10.0
        if node.plugin.startswith("text."):
            base += 3.0
        return base
