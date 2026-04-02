import pytest

from plugins.pack.routing import GatePlugin, SwitchPlugin


@pytest.mark.asyncio
async def test_route_switch_plugin():
    plugin = SwitchPlugin()
    result = await plugin.run({"key": "a", "routes": {"a": 1}, "default": 0})
    assert result["value"] == 1


@pytest.mark.asyncio
async def test_route_gate_plugin():
    plugin = GatePlugin()
    result = await plugin.run({"condition": False, "value": 3})
    assert result["value"] is None
