from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class HeadInput(BaseModel):
    values: List[Any]


class HeadOutput(BaseModel):
    value: Any


class HeadPlugin(Plugin):
    name = "collections.head"
    version = "1.0.0"
    description = "Returns the first element."
    input_model = HeadInput
    output_model = HeadOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        return {"value": values[0] if values else None}


class TailInput(BaseModel):
    values: List[Any]


class TailOutput(BaseModel):
    values: List[Any]


class TailPlugin(Plugin):
    name = "collections.tail"
    version = "1.0.0"
    description = "Returns all but the first element."
    input_model = TailInput
    output_model = TailOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"values": payload["values"][1:]}


class ChunkInput(BaseModel):
    values: List[Any]
    size: int


class ChunkOutput(BaseModel):
    chunks: List[List[Any]]


class ChunkPlugin(Plugin):
    name = "collections.chunk"
    version = "1.0.0"
    description = "Chunks a list into fixed sizes."
    input_model = ChunkInput
    output_model = ChunkOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        size = max(payload["size"], 1)
        values = payload["values"]
        chunks = [values[i : i + size] for i in range(0, len(values), size)]
        return {"chunks": chunks}


class FlattenInput(BaseModel):
    values: List[List[Any]]


class FlattenOutput(BaseModel):
    values: List[Any]


class FlattenPlugin(Plugin):
    name = "collections.flatten"
    version = "1.0.0"
    description = "Flattens a list of lists."
    input_model = FlattenInput
    output_model = FlattenOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        flattened = [item for sub in payload["values"] for item in sub]
        return {"values": flattened}


class DedupInput(BaseModel):
    values: List[Any]


class DedupOutput(BaseModel):
    values: List[Any]


class DedupPlugin(Plugin):
    name = "collections.dedup"
    version = "1.0.0"
    description = "Deduplicates a list while preserving order."
    input_model = DedupInput
    output_model = DedupOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        seen = set()
        output = []
        for value in payload["values"]:
            key = str(value)
            if key not in seen:
                output.append(value)
                seen.add(key)
        return {"values": output}


def register_collection_plugins(registry) -> None:
    registry.register(HeadPlugin(), capabilities=["collections:head"])
    registry.register(TailPlugin(), capabilities=["collections:tail"])
    registry.register(ChunkPlugin(), capabilities=["collections:chunk"])
    registry.register(FlattenPlugin(), capabilities=["collections:flatten"])
    registry.register(DedupPlugin(), capabilities=["collections:dedup"])
