from __future__ import annotations

import json
from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class JsonParseInput(BaseModel):
    raw: str


class JsonParseOutput(BaseModel):
    data: Dict[str, Any]


class JsonParsePlugin(Plugin):
    name = "json.parse"
    version = "1.0.0"
    description = "Parses JSON from a string."
    input_model = JsonParseInput
    output_model = JsonParseOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"data": json.loads(payload["raw"])}


class JsonSerializeInput(BaseModel):
    data: Dict[str, Any]


class JsonSerializeOutput(BaseModel):
    raw: str


class JsonSerializePlugin(Plugin):
    name = "json.serialize"
    version = "1.0.0"
    description = "Serializes JSON into a string."
    input_model = JsonSerializeInput
    output_model = JsonSerializeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"raw": json.dumps(payload["data"], sort_keys=True)}


class JsonPickInput(BaseModel):
    data: Dict[str, Any]
    keys: List[str]


class JsonPickOutput(BaseModel):
    data: Dict[str, Any]


class JsonPickPlugin(Plugin):
    name = "json.pick"
    version = "1.0.0"
    description = "Selects a subset of JSON keys."
    input_model = JsonPickInput
    output_model = JsonPickOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = payload["data"]
        keys = payload["keys"]
        return {"data": {key: data.get(key) for key in keys}}


class JsonMergeInput(BaseModel):
    base: Dict[str, Any]
    overlay: Dict[str, Any]


class JsonMergeOutput(BaseModel):
    data: Dict[str, Any]


class JsonMergePlugin(Plugin):
    name = "json.merge"
    version = "1.0.0"
    description = "Merges two JSON objects."
    input_model = JsonMergeInput
    output_model = JsonMergeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(payload["base"])
        merged.update(payload["overlay"])
        return {"data": merged}


class JsonDiffInput(BaseModel):
    source: Dict[str, Any]
    target: Dict[str, Any]


class JsonDiffOutput(BaseModel):
    added: Dict[str, Any]
    removed: List[str]
    changed: Dict[str, Dict[str, Any]]


class JsonDiffPlugin(Plugin):
    name = "json.diff"
    version = "1.0.0"
    description = "Computes a shallow diff between JSON objects."
    input_model = JsonDiffInput
    output_model = JsonDiffOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source = payload["source"]
        target = payload["target"]
        added = {k: v for k, v in target.items() if k not in source}
        removed = [k for k in source if k not in target]
        changed = {
            k: {"from": source[k], "to": target[k]}
            for k in source
            if k in target and source[k] != target[k]
        }
        return {"added": added, "removed": removed, "changed": changed}


def register_json_plugins(registry) -> None:
    registry.register(JsonParsePlugin(), capabilities=["json:parse"])
    registry.register(JsonSerializePlugin(), capabilities=["json:serialize"])
    registry.register(JsonPickPlugin(), capabilities=["json:pick"])
    registry.register(JsonMergePlugin(), capabilities=["json:merge"])
    registry.register(JsonDiffPlugin(), capabilities=["json:diff"])
