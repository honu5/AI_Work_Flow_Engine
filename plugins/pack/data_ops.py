from __future__ import annotations

from statistics import median
from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class UniqueInput(BaseModel):
    values: List[str]


class UniqueOutput(BaseModel):
    values: List[str]


class UniquePlugin(Plugin):
    name = "data.unique"
    version = "1.0.0"
    description = "Returns unique values preserving order."
    input_model = UniqueInput
    output_model = UniqueOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        seen = set()
        output = []
        for value in payload["values"]:
            if value not in seen:
                output.append(value)
                seen.add(value)
        return {"values": output}


class SortInput(BaseModel):
    values: List[float]
    descending: bool = False


class SortOutput(BaseModel):
    values: List[float]


class SortPlugin(Plugin):
    name = "data.sort"
    version = "1.0.0"
    description = "Sorts numeric values."
    input_model = SortInput
    output_model = SortOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = sorted(payload["values"], reverse=payload.get("descending", False))
        return {"values": values}


class MedianInput(BaseModel):
    values: List[float]


class MedianOutput(BaseModel):
    median: float


class MedianPlugin(Plugin):
    name = "data.median"
    version = "1.0.0"
    description = "Calculates median of values."
    input_model = MedianInput
    output_model = MedianOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        if not values:
            return {"median": 0.0}
        return {"median": float(median(values))}


class GroupInput(BaseModel):
    values: List[Dict[str, Any]]
    key: str


class GroupOutput(BaseModel):
    groups: Dict[str, List[Dict[str, Any]]]


class GroupPlugin(Plugin):
    name = "data.group"
    version = "1.0.0"
    description = "Groups dictionaries by a key value."
    input_model = GroupInput
    output_model = GroupOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for item in payload["values"]:
            key = str(item.get(payload["key"]))
            groups.setdefault(key, []).append(item)
        return {"groups": groups}


class MapInput(BaseModel):
    values: List[Dict[str, Any]]
    key: str


class MapOutput(BaseModel):
    values: List[Any]


class MapPlugin(Plugin):
    name = "data.map"
    version = "1.0.0"
    description = "Maps dictionaries to a specific key value."
    input_model = MapInput
    output_model = MapOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = [item.get(payload["key"]) for item in payload["values"]]
        return {"values": values}


def register_data_plugins(registry) -> None:
    registry.register(UniquePlugin(), capabilities=["data:unique"])
    registry.register(SortPlugin(), capabilities=["data:sort"])
    registry.register(MedianPlugin(), capabilities=["data:median"])
    registry.register(GroupPlugin(), capabilities=["data:group"])
    registry.register(MapPlugin(), capabilities=["data:map"])
