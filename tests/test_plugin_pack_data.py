import pytest

from plugins.pack.data_ops import UniquePlugin


@pytest.mark.asyncio
async def test_data_unique_plugin():
    plugin = UniquePlugin()
    result = await plugin.run({"values": ["a", "a", "b"]})
    assert result["values"] == ["a", "b"]
