from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class TruncateInput(BaseModel):
    text: str
    max_length: int = Field(ge=1)


class TruncateOutput(BaseModel):
    text: str
    truncated: bool


class TruncatePlugin(Plugin):
    name = "transform.truncate"
    version = "1.0.0"
    description = "Truncates text to a maximum length."
    input_model = TruncateInput
    output_model = TruncateOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"]
        limit = payload["max_length"]
        if len(text) <= limit:
            return {"text": text, "truncated": False}
        return {"text": text[:limit], "truncated": True}


class PadInput(BaseModel):
    text: str
    width: int = Field(ge=1)
    char: str = " "
    align: str = "left"


class PadOutput(BaseModel):
    text: str


class PadPlugin(Plugin):
    name = "transform.pad"
    version = "1.0.0"
    description = "Pads text to a fixed width."
    input_model = PadInput
    output_model = PadOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"]
        width = payload["width"]
        char = (payload.get("char") or " ")[:1]
        align = payload.get("align", "left")
        if len(text) >= width:
            return {"text": text[:width]}
        padding = char * (width - len(text))
        if align == "right":
            return {"text": padding + text}
        if align == "center":
            left = len(padding) // 2
            return {"text": padding[:left] + text + padding[left:]}
        return {"text": text + padding}


class SlugifyInput(BaseModel):
    text: str
    separator: str = "-"


class SlugifyOutput(BaseModel):
    slug: str


class SlugifyPlugin(Plugin):
    name = "transform.slugify"
    version = "1.0.0"
    description = "Creates a URL-friendly slug."
    input_model = SlugifyInput
    output_model = SlugifyOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"].lower().strip()
        sep = payload.get("separator", "-")
        cleaned = re.sub(r"[^a-z0-9]+", sep, text)
        slug = cleaned.strip(sep)
        return {"slug": slug or "item"}


class CoerceIntInput(BaseModel):
    value: Any
    default: int = 0


class CoerceIntOutput(BaseModel):
    value: int


class CoerceIntPlugin(Plugin):
    name = "transform.coerce_int"
    version = "1.0.0"
    description = "Coerces a value to integer with fallback."
    input_model = CoerceIntInput
    output_model = CoerceIntOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw = payload["value"]
        try:
            return {"value": int(raw)}
        except (TypeError, ValueError):
            return {"value": payload.get("default", 0)}


class CoerceFloatInput(BaseModel):
    value: Any
    default: float = 0.0


class CoerceFloatOutput(BaseModel):
    value: float


class CoerceFloatPlugin(Plugin):
    name = "transform.coerce_float"
    version = "1.0.0"
    description = "Coerces a value to float with fallback."
    input_model = CoerceFloatInput
    output_model = CoerceFloatOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw = payload["value"]
        try:
            return {"value": float(raw)}
        except (TypeError, ValueError):
            return {"value": float(payload.get("default", 0.0))}


class ReplaceCharsInput(BaseModel):
    text: str
    mapping: Dict[str, str] = Field(default_factory=dict)


class ReplaceCharsOutput(BaseModel):
    text: str


class ReplaceCharsPlugin(Plugin):
    name = "transform.replace_chars"
    version = "1.0.0"
    description = "Replaces characters using a mapping table."
    input_model = ReplaceCharsInput
    output_model = ReplaceCharsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"]
        for old, new in payload.get("mapping", {}).items():
            text = text.replace(old, new)
        return {"text": text}


class WrapColumnsInput(BaseModel):
    text: str
    width: int = Field(ge=10)


class WrapColumnsOutput(BaseModel):
    lines: List[str]


class WrapColumnsPlugin(Plugin):
    name = "transform.wrap_columns"
    version = "1.0.0"
    description = "Wraps text into fixed-width lines."
    input_model = WrapColumnsInput
    output_model = WrapColumnsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        width = payload["width"]
        words = payload["text"].split()
        lines: List[str] = []
        current: List[str] = []
        length = 0
        for word in words:
            extra = len(word) + (1 if current else 0)
            if length + extra > width and current:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += extra
        if current:
            lines.append(" ".join(current))
        return {"lines": lines or [""]}


def register_transform_plugins(registry) -> None:
    registry.register(TruncatePlugin(), capabilities=["transform:truncate"])
    registry.register(PadPlugin(), capabilities=["transform:pad"])
    registry.register(SlugifyPlugin(), capabilities=["transform:slugify"])
    registry.register(CoerceIntPlugin(), capabilities=["transform:coerce_int"])
    registry.register(CoerceFloatPlugin(), capabilities=["transform:coerce_float"])
    registry.register(ReplaceCharsPlugin(), capabilities=["transform:replace_chars"])
    registry.register(WrapColumnsPlugin(), capabilities=["transform:wrap_columns"])
