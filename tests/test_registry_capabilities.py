import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry


class CapPlugin(Plugin):
    name = "cap"
    version = "1.0.0"
    description = "cap"

    async def run(self, payload):
        return {"ok": True}


def test_registry_records_capabilities(repository):
    registry = PluginRegistry(repository)
    registry.register(CapPlugin(), capabilities=["core:test"])
    plugins = repository.list_plugins()
    assert plugins[0]["name"] == "cap"
    caps = repository.list_plugin_capabilities("cap")
    assert "core:test" in caps
