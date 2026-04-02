import pytest

from plugins.pack.encoding import Base64EncodePlugin
from plugins.pack.records import PickFieldPlugin
from plugins.pack.statistics import StatsSummaryPlugin
from plugins.pack.strings import WordCountPlugin


@pytest.mark.asyncio
async def test_stats_summary():
    plugin = StatsSummaryPlugin()
    result = await plugin.run({"values": [1, 2, 3, 4]})
    assert result["mean"] == 2.5


@pytest.mark.asyncio
async def test_base64_roundtrip():
    plugin = Base64EncodePlugin()
    encoded = await plugin.run({"text": "workflow"})
    from plugins.pack.encoding import Base64DecodePlugin

    decoded = await Base64DecodePlugin().run(encoded)
    assert decoded["text"] == "workflow"


@pytest.mark.asyncio
async def test_records_pick_field():
    plugin = PickFieldPlugin()
    result = await plugin.run(
        {
            "records": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}],
            "field": "name",
        }
    )
    assert result["values"] == ["a", "b"]


@pytest.mark.asyncio
async def test_strings_word_count():
    plugin = WordCountPlugin()
    result = await plugin.run({"text": "one two three"})
    assert result["count"] == 3
