import pytest

from plugins.pack.time_ops import WindowPlugin


@pytest.mark.asyncio
async def test_time_window_plugin():
    plugin = WindowPlugin()
    result = await plugin.run({"start": "2024-01-01T00:00:00", "end": "2024-01-01T00:00:10"})
    assert result["seconds"] == 10
