import pytest

from plugins.base import Plugin
from plugins.registry import PluginRegistry


class DummyPlugin(Plugin):
    name = "dummy"
    version = "1.0.0"
    description = "dummy"

    async def run(self, payload):
        return {"ok": True}


class DummyPluginV2(Plugin):
    name = "dummy"
    version = "2.0.0"
    description = "dummy v2"

    async def run(self, payload):
        return {"ok": True}


def test_register_conflict(repository):
    registry = PluginRegistry(repository)
    registry.register(DummyPlugin())
    with pytest.raises(ValueError):
        registry.register(DummyPluginV2())
