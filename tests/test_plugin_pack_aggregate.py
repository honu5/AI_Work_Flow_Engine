import pytest

from plugins.pack.aggregate import CountByPlugin, GroupSumPlugin, TopNPlugin


@pytest.mark.asyncio
async def test_count_by_plugin():
    plugin = CountByPlugin()
    result = await plugin.run(
        {
            "records": [{"team": "a"}, {"team": "b"}, {"team": "a"}],
            "field": "team",
        }
    )
    assert result["counts"]["a"] == 2


@pytest.mark.asyncio
async def test_top_n_plugin():
    plugin = TopNPlugin()
    result = await plugin.run(
        {
            "records": [{"score": 1}, {"score": 9}, {"score": 4}],
            "field": "score",
            "n": 2,
        }
    )
    assert result["items"][0]["score"] == 9


@pytest.mark.asyncio
async def test_group_sum_plugin():
    plugin = GroupSumPlugin()
    result = await plugin.run(
        {
            "records": [{"region": "us", "amount": 10}, {"region": "eu", "amount": 5}, {"region": "us", "amount": 3}],
            "group_field": "region",
            "value_field": "amount",
        }
    )
    assert result["groups"]["us"] == 13.0
