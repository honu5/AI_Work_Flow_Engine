import pytest

from plugins.pack.validation_ops import EmailPlugin, RequiredKeysPlugin


@pytest.mark.asyncio
async def test_validation_required_keys():
    plugin = RequiredKeysPlugin()
    result = await plugin.run({"data": {"a": 1}, "keys": ["a", "b"]})
    assert result["missing"] == ["b"]


@pytest.mark.asyncio
async def test_validation_email():
    plugin = EmailPlugin()
    result = await plugin.run({"value": "test@example.com"})
    assert result["valid"] is True
