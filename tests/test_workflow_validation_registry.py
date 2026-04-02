import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry
from workflows.schema import WorkflowNode
from workflows.validation import WorkflowValidator


class DummyPlugin(Plugin):
    name = "dummy"
    version = "1.0.0"
    description = "dummy"

    async def run(self, payload):
        return {"ok": True}


def test_validator_checks_registry(repository):
    registry = PluginRegistry(repository)
    registry.register(DummyPlugin())
    validator = WorkflowValidator(registry)

    result = validator.validate([WorkflowNode(id="n1", plugin="dummy")])
    assert result.valid is True

    result = validator.validate([WorkflowNode(id="n2", plugin="missing")])
    assert result.valid is False
