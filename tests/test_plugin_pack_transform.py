import pytest

from plugins.pack.transform import PadPlugin, SlugifyPlugin, TruncatePlugin, WrapColumnsPlugin


@pytest.mark.asyncio
async def test_truncate_plugin():
    plugin = TruncatePlugin()
    result = await plugin.run({"text": "abcdef", "max_length": 4})
    assert result["text"] == "abcd"
    assert result["truncated"] is True


@pytest.mark.asyncio
async def test_slugify_plugin():
    plugin = SlugifyPlugin()
    result = await plugin.run({"text": "Hello World!", "separator": "-"})
    assert result["slug"] == "hello-world"


@pytest.mark.asyncio
async def test_wrap_columns_plugin():
    plugin = WrapColumnsPlugin()
    result = await plugin.run({"text": "one two three four five", "width": 10})
    assert len(result["lines"]) >= 2


@pytest.mark.asyncio
async def test_pad_plugin_center():
    plugin = PadPlugin()
    result = await plugin.run({"text": "x", "width": 5, "align": "center"})
    assert len(result["text"]) == 5
