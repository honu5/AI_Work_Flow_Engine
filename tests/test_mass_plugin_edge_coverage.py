import pytest

from plugins.pack.aggregate import (
    CountByPlugin,
    GroupSumPlugin,
    MergeDictsPlugin,
    SumFieldPlugin,
    TopNPlugin,
)
from plugins.pack.datetime_parse import (
    AddDurationPlugin,
    DiffSecondsPlugin,
    ParseIsoPlugin,
)
from plugins.pack.encoding import (
    Base64DecodePlugin,
    Base64EncodePlugin,
    HexDecodePlugin,
    HexEncodePlugin,
    JsonPrettyPlugin,
    UrlDecodePlugin,
    UrlEncodePlugin,
)
from plugins.pack.records import (
    CoalescePlugin,
    FilterRecordsPlugin,
    GroupRecordsPlugin,
    PickFieldPlugin,
    ProjectPlugin,
    SortRecordsPlugin,
)
from plugins.pack.statistics import (
    CorrelationPlugin,
    HistogramPlugin,
    MovingAveragePlugin,
    PercentilePlugin,
    StatsSummaryPlugin,
    ZScorePlugin,
)
from plugins.pack.strings import (
    ExtractNumbersPlugin,
    JoinLinesPlugin,
    PrefixSuffixPlugin,
    RegexFindPlugin,
    RegexReplacePlugin,
    SplitLinesPlugin,
    TruncateWordsPlugin,
    WordCountPlugin,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected_mean,expected_count",
    [
        ({"values": [1, 2, 3, 4]}, 2.5, 4),
        ({"values": [10, 10, 10]}, 10.0, 3),
        ({"values": [-1, 0, 1]}, 0.0, 3),
        ({"values": [100]}, 100.0, 1),
        ({"values": []}, 0.0, 0),
    ],
)
async def test_stats_summary_edges(payload, expected_mean, expected_count):
    result = await StatsSummaryPlugin().run(payload)
    assert result["mean"] == expected_mean
    assert result["count"] == expected_count


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"values": [1, 2, 3, 4, 5], "percentile": 0}, 1.0),
        ({"values": [1, 2, 3, 4, 5], "percentile": 50}, 3.0),
        ({"values": [1, 2, 3, 4, 5], "percentile": 100}, 5.0),
        ({"values": [5, 1, 3], "percentile": 25}, 2.0),
        ({"values": [], "percentile": 50}, 0.0),
    ],
)
async def test_percentile_edges(payload, expected):
    result = await PercentilePlugin().run(payload)
    assert result["value"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"values": [1, 2, 3, 4], "target": 4}, 1.3416407864998738),
        ({"values": [10, 10, 10], "target": 10}, 0.0),
        ({"values": [5], "target": 7}, 0.0),
        ({"values": [1, 2], "target": 1}, -1.0),
    ],
)
async def test_z_score_edges(payload, expected):
    result = await ZScorePlugin().run(payload)
    assert pytest.approx(result["z_score"], rel=1e-9, abs=1e-9) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected_len",
    [
        ({"values": [1, 2, 3, 4], "bins": 2}, 2),
        ({"values": [1, 1, 1], "bins": 3}, 3),
        ({"values": [0, 10], "bins": 5}, 5),
        ({"values": [], "bins": 4}, 0),
    ],
)
async def test_histogram_edges(payload, expected_len):
    result = await HistogramPlugin().run(payload)
    assert len(result["bins"]) == expected_len


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected_last",
    [
        ({"values": [1, 2, 3, 4], "window": 2}, 3.5),
        ({"values": [10, 20, 30], "window": 5}, 20.0),
        ({"values": [5], "window": 1}, 5.0),
        ({"values": [], "window": 3}, None),
    ],
)
async def test_moving_average_edges(payload, expected_last):
    result = await MovingAveragePlugin().run(payload)
    if expected_last is None:
        assert result["values"] == []
    else:
        assert result["values"][-1] == expected_last


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"xs": [1, 2, 3], "ys": [1, 2, 3]}, 1.0),
        ({"xs": [1, 2, 3], "ys": [3, 2, 1]}, -1.0),
        ({"xs": [1, 1, 1], "ys": [2, 3, 4]}, 0.0),
        ({"xs": [1], "ys": [1]}, 0.0),
        ({"xs": [1, 2], "ys": [1]}, 0.0),
    ],
)
async def test_correlation_edges(payload, expected):
    result = await CorrelationPlugin().run(payload)
    assert pytest.approx(result["coefficient"], rel=1e-9, abs=1e-9) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text",
    ["simple", "workflow-engine", "1234", "Symbols !@#"],
)
async def test_encoding_roundtrips(text):
    b64 = await Base64EncodePlugin().run({"text": text})
    assert (await Base64DecodePlugin().run(b64))["text"] == text

    hx = await HexEncodePlugin().run({"text": text})
    assert (await HexDecodePlugin().run(hx))["text"] == text

    quoted = await UrlEncodePlugin().run({"text": text})
    assert (await UrlDecodePlugin().run(quoted))["text"] == text


@pytest.mark.asyncio
async def test_encoding_invalid_inputs():
    assert (await Base64DecodePlugin().run({"text": "!!!!"}))["text"] == ""
    assert (await HexDecodePlugin().run({"text": "zzzz"}))["text"] == ""
    assert (await JsonPrettyPlugin().run({"text": "not-json"}))["text"] == "not-json"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "records,field,expected",
    [
        ([{"id": 1}, {"id": 2}], "id", [1, 2]),
        ([{"name": "a"}, {"name": "b"}], "name", ["a", "b"]),
        ([{"x": 1}, {"y": 2}], "x", [1, None]),
    ],
)
async def test_records_pick_field_edges(records, field, expected):
    result = await PickFieldPlugin().run({"records": records, "field": field})
    assert result["values"] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "records,field,equals,expected_len",
    [
        ([{"a": 1}, {"a": 2}], "a", 1, 1),
        ([{"a": "x"}, {"a": "x"}], "a", "x", 2),
        ([{"a": 1}, {"b": 1}], "a", 1, 1),
        ([{"a": 1}, {"a": 2}], "a", 9, 0),
    ],
)
async def test_records_filter_edges(records, field, equals, expected_len):
    result = await FilterRecordsPlugin().run(
        {"records": records, "field": field, "equals": equals}
    )
    assert len(result["records"]) == expected_len


@pytest.mark.asyncio
async def test_records_project_group_sort_coalesce_edges():
    source = [{"k": "a", "v": 2}, {"k": "a", "v": 1}, {"k": "b", "v": 3}]

    projected = await ProjectPlugin().run({"records": source, "fields": ["k"]})
    assert projected["records"] == [{"k": "a"}, {"k": "a"}, {"k": "b"}]

    grouped = await GroupRecordsPlugin().run({"records": source, "field": "k"})
    assert set(grouped["groups"]) == {"a", "b"}

    sorted_rows = await SortRecordsPlugin().run(
        {"records": source, "field": "v", "descending": True}
    )
    assert sorted_rows["records"][0]["v"] == 3

    picked = await CoalescePlugin().run(
        {"record": {"x": None, "y": "ok"}, "fields": ["x", "y"], "default": "d"}
    )
    assert picked["value"] == "ok"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text,expected_count",
    [
        ("one two three", 3),
        (" punctuation! and numbers 123 ", 4),
        ("", 0),
        ("repeat repeat repeat", 3),
    ],
)
async def test_strings_word_count_edges(text, expected_count):
    result = await WordCountPlugin().run({"text": text})
    assert result["count"] == expected_count


@pytest.mark.asyncio
async def test_strings_regex_join_split_extract_and_affix():
    split = await SplitLinesPlugin().run({"text": "a\nb\nc"})
    assert split["lines"] == ["a", "b", "c"]

    joined = await JoinLinesPlugin().run({"lines": ["a", "b"], "separator": ":"})
    assert joined["text"] == "a:b"

    found = await RegexFindPlugin().run({"text": "a1 b2 c3", "pattern": r"\d"})
    assert found["matches"] == ["1", "2", "3"]

    replaced = await RegexReplacePlugin().run(
        {"text": "a1 b2", "pattern": r"\d", "replacement": "_"}
    )
    assert replaced["text"] == "a_ b_"

    nums = await ExtractNumbersPlugin().run({"text": "x -3 y 4.5 z 0"})
    assert nums["numbers"] == [-3, 4.5, 0]

    affix = await PrefixSuffixPlugin().run(
        {"text": "core", "prefix": "[", "suffix": "]"}
    )
    assert affix["text"] == "[core]"

    trunc = await TruncateWordsPlugin().run(
        {"text": "one two three four", "max_words": 2}
    )
    assert trunc["text"] == "one two"


@pytest.mark.asyncio
async def test_aggregate_plugins_edges():
    records = [{"team": "a", "score": 3}, {"team": "b", "score": 4}, {"team": "a", "score": 1}]

    count = await CountByPlugin().run({"records": records, "field": "team"})
    assert count["counts"] == {"a": 2, "b": 1}

    top = await TopNPlugin().run({"records": records, "field": "score", "n": 2})
    assert [item["score"] for item in top["items"]] == [4, 3]

    summed = await SumFieldPlugin().run({"records": records, "field": "score"})
    assert summed["total"] == 8.0
    assert summed["count"] == 3

    grouped = await GroupSumPlugin().run(
        {"records": records, "group_field": "team", "value_field": "score"}
    )
    assert grouped["groups"] == {"a": 4.0, "b": 4.0}

    merged = await MergeDictsPlugin().run({"mappings": [{"a": 1}, {"b": 2}, {"a": 3}]})
    assert merged["merged"] == {"a": 3, "b": 2}


@pytest.mark.asyncio
async def test_datetime_plugins_edges():
    parsed = await ParseIsoPlugin().run({"value": "2026-01-02T03:04:05+00:00"})
    assert parsed["year"] == 2026
    assert parsed["month"] == 1
    assert parsed["day"] == 2

    shifted = await AddDurationPlugin().run(
        {"value": "2026-01-01T00:00:00+00:00", "days": 1, "hours": 2, "minutes": 3}
    )
    assert shifted["timestamp"].startswith("2026-01-02T02:03:00")

    diff = await DiffSecondsPlugin().run(
        {"start": "2026-01-01T00:00:00+00:00", "end": "2026-01-01T00:10:00+00:00"}
    )
    assert diff["seconds"] == 600.0
