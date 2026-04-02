from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class InputBlock:
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeDecl:
    node_id: str
    plugin: str
    input_block: InputBlock
    depends_on: List[str] = field(default_factory=list)


@dataclass
class WorkflowDecl:
    name: str
    nodes: List[NodeDecl] = field(default_factory=list)
