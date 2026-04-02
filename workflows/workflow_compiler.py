from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from plugins.registry import PluginRegistry
from workflows.graph import GraphNode, WorkflowGraph
from workflows.schema import WorkflowCreate, WorkflowNode
from workflows.validation import WorkflowValidator


@dataclass
class CompileDiagnostic:
    level: str
    message: str
    node_id: Optional[str] = None


@dataclass
class CompiledWorkflow:
    workflow: WorkflowCreate
    stages: List[List[str]]
    critical_path: List[str]
    diagnostics: List[CompileDiagnostic] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(d.level == "error" for d in self.diagnostics)


def compile_workflow(
    workflow: WorkflowCreate,
    registry: Optional[PluginRegistry] = None,
) -> CompiledWorkflow:
    diagnostics: List[CompileDiagnostic] = []
    validation = WorkflowValidator(registry).validate(workflow.nodes)
    for error in validation.errors:
        diagnostics.append(CompileDiagnostic(level="error", message=error))

    graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in workflow.nodes])
    if graph.has_cycle():
        diagnostics.append(CompileDiagnostic(level="error", message="Workflow graph contains a cycle"))

    stages = graph.levels()
    critical = graph.critical_path()

    for node in workflow.nodes:
        if node.timeout_seconds is not None and node.timeout_seconds <= 0:
            diagnostics.append(
                CompileDiagnostic(
                    level="error",
                    message="timeout_seconds must be positive",
                    node_id=node.id,
                )
            )
        if node.retry is not None:
            limit = node.retry.get("limit", 1)
            if limit < 1:
                diagnostics.append(
                    CompileDiagnostic(
                        level="error",
                        message="retry limit must be at least 1",
                        node_id=node.id,
                    )
                )

    for node in workflow.nodes:
        if len(node.depends_on) > 3:
            diagnostics.append(
                CompileDiagnostic(
                    level="warning",
                    message="Node has many upstream dependencies; consider splitting stages",
                    node_id=node.id,
                )
            )

    return CompiledWorkflow(
        workflow=workflow,
        stages=stages,
        critical_path=critical,
        diagnostics=diagnostics,
    )


def compile_workflow_dict(definition: Dict[str, Any], registry: Optional[PluginRegistry] = None) -> CompiledWorkflow:
    workflow = WorkflowCreate(**definition)
    return compile_workflow(workflow, registry=registry)
