import pytest

from plugins.pack.collections import ChunkPlugin, HeadPlugin


@pytest.mark.asyncio
async def test_collections_head_plugin():
    plugin = HeadPlugin()
    result = await plugin.run({"values": [1, 2, 3]})
    assert result["value"] == 1


@pytest.mark.asyncio
async def test_collections_chunk_plugin():
    plugin = ChunkPlugin()
    result = await plugin.run({"values": [1, 2, 3, 4], "size": 2})
    assert result["chunks"] == [[1, 2], [3, 4]]
