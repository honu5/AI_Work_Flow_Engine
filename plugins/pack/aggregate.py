from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class SumFieldInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str


class SumFieldOutput(BaseModel):
    total: float
    count: int


class SumFieldPlugin(Plugin):
    name = "aggregate.sum_field"
    version = "1.0.0"
    description = "Sums a numeric field across records."
    input_model = SumFieldInput
    output_model = SumFieldOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        total = 0.0
        count = 0
        for record in payload["records"]:
            value = record.get(payload["field"])
            if isinstance(value, (int, float)):
                total += float(value)
                count += 1
        return {"total": total, "count": count}


class CountByInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str


class CountByOutput(BaseModel):
    counts: Dict[str, int]


class CountByPlugin(Plugin):
    name = "aggregate.count_by"
    version = "1.0.0"
    description = "Counts records grouped by a field value."
    input_model = CountByInput
    output_model = CountByOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        counter: Counter[str] = Counter()
        for record in payload["records"]:
            key = str(record.get(payload["field"], "unknown"))
            counter[key] += 1
        return {"counts": dict(counter)}


class TopNInput(BaseModel):
    records: List[Dict[str, Any]]
    field: str
    n: int = Field(ge=1, le=100)


class TopNOutput(BaseModel):
    items: List[Dict[str, Any]]


class TopNPlugin(Plugin):
    name = "aggregate.top_n"
    version = "1.0.0"
    description = "Returns top N records by numeric field."
    input_model = TopNInput
    output_model = TopNOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        field = payload["field"]
        ranked = sorted(
            payload["records"],
            key=lambda item: float(item.get(field, 0)),
            reverse=True,
        )
        return {"items": ranked[: payload["n"]]}


class MergeDictsInput(BaseModel):
    mappings: List[Dict[str, Any]]


class MergeDictsOutput(BaseModel):
    merged: Dict[str, Any]


class MergeDictsPlugin(Plugin):
    name = "aggregate.merge_dicts"
    version = "1.0.0"
    description = "Merges dictionaries with later keys overriding earlier ones."
    input_model = MergeDictsInput
    output_model = MergeDictsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for mapping in payload["mappings"]:
            merged.update(mapping)
        return {"merged": merged}


class GroupSumInput(BaseModel):
    records: List[Dict[str, Any]]
    group_field: str
    value_field: str


class GroupSumOutput(BaseModel):
    groups: Dict[str, float]


class GroupSumPlugin(Plugin):
    name = "aggregate.group_sum"
    version = "1.0.0"
    description = "Sums a numeric field grouped by another field."
    input_model = GroupSumInput
    output_model = GroupSumOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        totals: Dict[str, float] = defaultdict(float)
        for record in payload["records"]:
            group = str(record.get(payload["group_field"], "default"))
            value = record.get(payload["value_field"], 0)
            if isinstance(value, (int, float)):
                totals[group] += float(value)
        return {"groups": dict(totals)}


def register_aggregate_plugins(registry) -> None:
    registry.register(SumFieldPlugin(), capabilities=["aggregate:sum"])
    registry.register(CountByPlugin(), capabilities=["aggregate:count_by"])
    registry.register(TopNPlugin(), capabilities=["aggregate:top_n"])
    registry.register(MergeDictsPlugin(), capabilities=["aggregate:merge"])
    registry.register(GroupSumPlugin(), capabilities=["aggregate:group_sum"])
