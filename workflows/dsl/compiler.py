from __future__ import annotations

from workflows.dsl.ast_nodes import WorkflowDecl
from workflows.dsl.parser import WorkflowDslParser
from workflows.schema import WorkflowCreate, WorkflowNode


def compile_dsl(text: str) -> WorkflowCreate:
    decl = WorkflowDslParser(text).parse()
    return workflow_decl_to_create(decl)


def workflow_decl_to_create(decl: WorkflowDecl) -> WorkflowCreate:
    nodes = [
        WorkflowNode(
            id=node.node_id,
            plugin=node.plugin,
            input=dict(node.input_block.values),
            depends_on=list(node.depends_on),
        )
        for node in decl.nodes
    ]
    return WorkflowCreate(name=decl.name, nodes=nodes)
