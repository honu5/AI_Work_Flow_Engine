import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowNode
from workflows.validation import WorkflowValidator


class CapPlugin(Plugin):
    name = "cap"
    version = "1.0.0"
    description = "cap"

    async def run(self, payload):
        return payload


def test_validator_requires_capability(repository):
    registry = PluginRegistry(repository)
    registry.register(CapPlugin(), capabilities=["core:one"])
    validator = WorkflowValidator(registry)

    node = WorkflowNode(id="n1", plugin="cap", requires=["core:one"])
    assert validator.validate([node]).valid is True

    node_missing = WorkflowNode(id="n2", plugin="cap", requires=["core:two"])
    assert validator.validate([node_missing]).valid is False
