import pytest

from plugins.pack.data_ops import GroupPlugin, MapPlugin
from plugins.pack.json_ops import JsonMergePlugin
from plugins.pack.math import ClampPlugin
from plugins.pack.text import NgramPlugin
from plugins.pack.time_ops import FormatPlugin


@pytest.mark.asyncio
async def test_text_ngram_plugin():
    plugin = NgramPlugin()
    result = await plugin.run({"tokens": ["a", "b", "c"], "size": 2})
    assert result["ngrams"] == ["a b", "b c"]


@pytest.mark.asyncio
async def test_math_clamp_plugin():
    plugin = ClampPlugin()
    result = await plugin.run({"value": 10, "minimum": 0, "maximum": 5})
    assert result["value"] == 5


@pytest.mark.asyncio
async def test_json_merge_plugin():
    plugin = JsonMergePlugin()
    result = await plugin.run({"base": {"a": 1}, "overlay": {"b": 2}})
    assert result["data"] == {"a": 1, "b": 2}


@pytest.mark.asyncio
async def test_time_format_plugin():
    plugin = FormatPlugin()
    result = await plugin.run({"timestamp": "2024-01-01T00:00:00", "format": "%Y"})
    assert result["formatted"] == "2024"


@pytest.mark.asyncio
async def test_data_group_plugin():
    plugin = GroupPlugin()
    result = await plugin.run(
        {"values": [{"k": "a"}, {"k": "b"}, {"k": "a"}], "key": "k"}
    )
    assert "a" in result["groups"]


@pytest.mark.asyncio
async def test_data_map_plugin():
    plugin = MapPlugin()
    result = await plugin.run({"values": [{"k": 1}, {"k": 2}], "key": "k"})
    assert result["values"] == [1, 2]
