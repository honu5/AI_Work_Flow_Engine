from __future__ import annotations

import pytest

from plugins.pack.analysis import ChunkListPlugin, KeywordDensityPlugin, NumericProfilePlugin, SectionIndexPlugin


@pytest.mark.asyncio
async def test_keyword_density_plugin():
    plugin = KeywordDensityPlugin()
    result = await plugin.run({"text": "alpha beta alpha gamma", "keywords": ["alpha", "beta"]})
    assert result["total_words"] == 4
    assert result["matches"]["alpha"] == 2
    assert result["density"]["alpha"] == 0.5


@pytest.mark.asyncio
async def test_numeric_profile_plugin():
    plugin = NumericProfilePlugin()
    result = await plugin.run({"values": [1, 2, 3, 4]})
    assert result["count"] == 4
    assert result["minimum"] == 1
    assert result["maximum"] == 4
    assert result["average"] == 2.5


@pytest.mark.asyncio
async def test_chunk_list_plugin():
    plugin = ChunkListPlugin()
    result = await plugin.run({"items": [1, 2, 3, 4, 5], "chunk_size": 2})
    assert result["chunks"] == [[1, 2], [3, 4], [5]]


@pytest.mark.asyncio
async def test_section_index_plugin():
    plugin = SectionIndexPlugin()
    result = await plugin.run({"text": "# Intro\ntext\n## Details\nmore"})
    assert result["sections"] == ["Intro", "Details"]
