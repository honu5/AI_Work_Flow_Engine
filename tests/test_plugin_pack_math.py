import pytest

from plugins.pack.math import AveragePlugin, SumPlugin


@pytest.mark.asyncio
async def test_math_sum_plugin():
    plugin = SumPlugin()
    result = await plugin.run({"values": [1, 2, 3]})
    assert result["total"] == 6.0


@pytest.mark.asyncio
async def test_math_average_plugin():
    plugin = AveragePlugin()
    result = await plugin.run({"values": [2, 4, 6]})
    assert result["average"] == 4.0
