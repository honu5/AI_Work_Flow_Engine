import pytest

from plugins.pack.formatting import JoinPlugin, SplitPlugin


@pytest.mark.asyncio
async def test_format_join_plugin():
    plugin = JoinPlugin()
    result = await plugin.run({"values": ["a", "b"], "separator": "-"})
    assert result["text"] == "a-b"


@pytest.mark.asyncio
async def test_format_split_plugin():
    plugin = SplitPlugin()
    result = await plugin.run({"text": "a,b", "separator": ","})
    assert result["values"] == ["a", "b"]
