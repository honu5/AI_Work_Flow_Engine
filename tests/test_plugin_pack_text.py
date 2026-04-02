import pytest

from plugins.pack.text import NormalizeTextPlugin, TokenizePlugin
from plugins.validation import validate_input, validate_output


@pytest.mark.asyncio
async def test_text_normalize_plugin():
    plugin = NormalizeTextPlugin()
    payload = validate_input(plugin, {"text": "  HeLLo "})
    result = await plugin.run(payload)
    result = validate_output(plugin, result)
    assert result["text"] == "hello"


@pytest.mark.asyncio
async def test_text_tokenize_plugin():
    plugin = TokenizePlugin()
    payload = validate_input(plugin, {"text": "hi there"})
    result = await plugin.run(payload)
    assert result["tokens"] == ["hi", "there"]
