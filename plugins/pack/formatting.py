from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class JoinInput(BaseModel):
    values: List[str]
    separator: str = ","


class JoinOutput(BaseModel):
    text: str


class JoinPlugin(Plugin):
    name = "format.join"
    version = "1.0.0"
    description = "Joins a list of strings."
    input_model = JoinInput
    output_model = JoinOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": payload.get("separator", ",").join(payload["values"])}


class SplitInput(BaseModel):
    text: str
    separator: str = ","


class SplitOutput(BaseModel):
    values: List[str]


class SplitPlugin(Plugin):
    name = "format.split"
    version = "1.0.0"
    description = "Splits a string into values."
    input_model = SplitInput
    output_model = SplitOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"values": payload["text"].split(payload.get("separator", ","))}


class PadInput(BaseModel):
    text: str
    width: int
    char: str = " "


class PadOutput(BaseModel):
    text: str


class PadPlugin(Plugin):
    name = "format.pad"
    version = "1.0.0"
    description = "Pads a string to a fixed width."
    input_model = PadInput
    output_model = PadOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        width = payload["width"]
        char = payload.get("char", " ")
        text = payload["text"]
        if len(char) != 1:
            char = " "
        return {"text": text.ljust(width, char)}


class TruncateInput(BaseModel):
    text: str
    limit: int


class TruncateOutput(BaseModel):
    text: str


class TruncatePlugin(Plugin):
    name = "format.truncate"
    version = "1.0.0"
    description = "Truncates text to a fixed length."
    input_model = TruncateInput
    output_model = TruncateOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        limit = max(payload["limit"], 0)
        return {"text": payload["text"][:limit]}


class WrapInput(BaseModel):
    text: str
    width: int


class WrapOutput(BaseModel):
    lines: List[str]


class WrapPlugin(Plugin):
    name = "format.wrap"
    version = "1.0.0"
    description = "Wraps text into lines."
    input_model = WrapInput
    output_model = WrapOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        width = max(payload["width"], 1)
        text = payload["text"]
        lines = [text[i : i + width] for i in range(0, len(text), width)]
        return {"lines": lines}


def register_formatting_plugins(registry) -> None:
    registry.register(JoinPlugin(), capabilities=["format:join"])
    registry.register(SplitPlugin(), capabilities=["format:split"])
    registry.register(PadPlugin(), capabilities=["format:pad"])
    registry.register(TruncatePlugin(), capabilities=["format:truncate"])
    registry.register(WrapPlugin(), capabilities=["format:wrap"])
