import pytest

from plugins.pack.logic import AnyPlugin, ComparePlugin


@pytest.mark.asyncio
async def test_logic_any_plugin():
    plugin = AnyPlugin()
    result = await plugin.run({"values": [False, True]})
    assert result["result"] is True


@pytest.mark.asyncio
async def test_logic_compare_plugin():
    plugin = ComparePlugin()
    result = await plugin.run({"left": 1, "right": 2, "op": "<"})
    assert result["result"] is True
