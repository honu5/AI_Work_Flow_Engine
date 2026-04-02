import json

import pytest

from plugins.pack.json_ops import JsonDiffPlugin, JsonParsePlugin


@pytest.mark.asyncio
async def test_json_parse_plugin():
    plugin = JsonParsePlugin()
    result = await plugin.run({"raw": json.dumps({"a": 1})})
    assert result["data"]["a"] == 1


@pytest.mark.asyncio
async def test_json_diff_plugin():
    plugin = JsonDiffPlugin()
    result = await plugin.run({"source": {"a": 1}, "target": {"a": 2, "b": 3}})
    assert result["added"] == {"b": 3}
    assert result["changed"]["a"]["to"] == 2
