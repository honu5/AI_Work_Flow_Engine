from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Set

from workflows.graph import GraphNode, WorkflowGraph
from workflows.schema import WorkflowNode


@dataclass
class LintIssue:
    rule: str
    severity: str
    message: str
    node_id: str | None = None


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    def ok(self) -> bool:
        return self.error_count == 0


class WorkflowLinter:
    """Static analysis for workflow definitions before execution."""

    def lint(self, nodes: Iterable[WorkflowNode]) -> LintReport:
        report = LintReport()
        node_list = list(nodes)
        self._check_duplicate_ids(node_list, report)
        self._check_unknown_dependencies(node_list, report)
        self._check_cycles(node_list, report)
        self._check_unreachable_nodes(node_list, report)
        self._check_empty_plugins(node_list, report)
        self._check_retry_configuration(node_list, report)
        self._check_timeout_configuration(node_list, report)
        self._check_redundant_dependencies(node_list, report)
        self._check_fan_in_complexity(node_list, report)
        return report

    def _check_duplicate_ids(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        seen: Set[str] = set()
        for node in nodes:
            if node.id in seen:
                report.issues.append(
                    LintIssue(
                        rule="duplicate_id",
                        severity="error",
                        message=f"Duplicate node id {node.id}",
                        node_id=node.id,
                    )
                )
            seen.add(node.id)

    def _check_unknown_dependencies(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        known = {node.id for node in nodes}
        for node in nodes:
            for dep in node.depends_on:
                if dep not in known:
                    report.issues.append(
                        LintIssue(
                            rule="unknown_dependency",
                            severity="error",
                            message=f"Node {node.id} depends on unknown node {dep}",
                            node_id=node.id,
                        )
                    )

    def _check_cycles(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in nodes])
        if graph.has_cycle():
            report.issues.append(
                LintIssue(
                    rule="cycle",
                    severity="error",
                    message="Workflow contains a dependency cycle",
                )
            )

    def _check_unreachable_nodes(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        if not nodes:
            return
        graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in nodes])
        reachable: Set[str] = set()
        roots = [node.id for node in nodes if not node.depends_on]
        if not roots:
            roots = [nodes[0].id]
        stack = list(roots)
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            for downstream, node in ((n.id, n) for n in nodes):
                if current in node.depends_on:
                    stack.append(downstream)
        for node in nodes:
            if node.id not in reachable:
                report.issues.append(
                    LintIssue(
                        rule="unreachable",
                        severity="warning",
                        message=f"Node {node.id} is not reachable from workflow roots",
                        node_id=node.id,
                    )
                )

    def _check_empty_plugins(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        for node in nodes:
            if not node.plugin.strip():
                report.issues.append(
                    LintIssue(
                        rule="empty_plugin",
                        severity="error",
                        message="Plugin name must not be empty",
                        node_id=node.id,
                    )
                )

    def _check_retry_configuration(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        for node in nodes:
            if not node.retry:
                continue
            limit = node.retry.get("limit", 1)
            backoff = node.retry.get("backoff", 0)
            if limit < 1:
                report.issues.append(
                    LintIssue(
                        rule="retry_limit",
                        severity="error",
                        message="Retry limit must be >= 1",
                        node_id=node.id,
                    )
                )
            if backoff < 0:
                report.issues.append(
                    LintIssue(
                        rule="retry_backoff",
                        severity="error",
                        message="Retry backoff must be non-negative",
                        node_id=node.id,
                    )
                )

    def _check_timeout_configuration(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        for node in nodes:
            if node.timeout_seconds is not None and node.timeout_seconds <= 0:
                report.issues.append(
                    LintIssue(
                        rule="timeout",
                        severity="error",
                        message="timeout_seconds must be positive when set",
                        node_id=node.id,
                    )
                )

    def _check_redundant_dependencies(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        graph = WorkflowGraph([GraphNode(node.id, node.depends_on) for node in nodes])
        for node in nodes:
            deps = set(node.depends_on)
            redundant = set()
            for dep in deps:
                for other in deps:
                    if dep == other:
                        continue
                    if dep in graph.dependencies(other) or self._transitive(graph, other, dep):
                        redundant.add(dep)
                        break
            for dep in sorted(redundant):
                report.issues.append(
                    LintIssue(
                        rule="redundant_dependency",
                        severity="warning",
                        message=f"Dependency {dep} on {node.id} is implied by other dependencies",
                        node_id=node.id,
                    )
                )

    def _transitive(self, graph: WorkflowGraph, start: str, target: str) -> bool:
        visited: Set[str] = set()
        stack = [start]
        while stack:
            current = stack.pop()
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(graph.dependencies(current))
        return False

    def _check_fan_in_complexity(self, nodes: List[WorkflowNode], report: LintReport) -> None:
        inbound: dict[str, int] = {node.id: 0 for node in nodes}
        for node in nodes:
            for dep in node.depends_on:
                inbound[node.id] = inbound.get(node.id, 0)
            for downstream in nodes:
                if node.id in downstream.depends_on:
                    inbound[downstream.id] = inbound.get(downstream.id, 0) + 1
        for node in nodes:
            count = sum(1 for other in nodes if node.id in other.depends_on)
            if count > 5:
                report.issues.append(
                    LintIssue(
                        rule="fan_in",
                        severity="warning",
                        message=f"Node {node.id} has {count} upstream dependencies",
                        node_id=node.id,
                    )
                )
