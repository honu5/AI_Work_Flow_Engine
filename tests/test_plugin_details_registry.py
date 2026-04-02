from plugins.base import Plugin
from plugins.registry import PluginRegistry


class DetailPlugin(Plugin):
    name = "detail"
    version = "1.0.0"
    description = "detail"

    async def run(self, payload):
        return payload


def test_registry_get_details(repository):
    registry = PluginRegistry(repository)
    registry.register(DetailPlugin(), capabilities=["detail:test"])
    details = registry.get_details("detail")
    assert "detail:test" in details["capabilities"]
