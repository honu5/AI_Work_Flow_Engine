from __future__ import annotations

import base64
import binascii
import json
from typing import Any, Dict
from urllib.parse import quote, unquote

from pydantic import BaseModel

from plugins.base import Plugin


class TextPayload(BaseModel):
    text: str


class TextResult(BaseModel):
    text: str


class Base64EncodePlugin(Plugin):
    name = "encoding.base64_encode"
    version = "1.0.0"
    description = "Encodes text to base64."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        encoded = base64.b64encode(payload["text"].encode("utf-8")).decode("ascii")
        return {"text": encoded}


class Base64DecodePlugin(Plugin):
    name = "encoding.base64_decode"
    version = "1.0.0"
    description = "Decodes base64 text."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            decoded = base64.b64decode(payload["text"]).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            decoded = ""
        return {"text": decoded}


class UrlEncodePlugin(Plugin):
    name = "encoding.url_encode"
    version = "1.0.0"
    description = "URL-encodes text."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": quote(payload["text"])}


class UrlDecodePlugin(Plugin):
    name = "encoding.url_decode"
    version = "1.0.0"
    description = "URL-decodes text."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": unquote(payload["text"])}


class HexEncodePlugin(Plugin):
    name = "encoding.hex_encode"
    version = "1.0.0"
    description = "Encodes UTF-8 bytes as hex."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": payload["text"].encode("utf-8").hex()}


class HexDecodePlugin(Plugin):
    name = "encoding.hex_decode"
    version = "1.0.0"
    description = "Decodes hex to UTF-8 text."
    input_model = TextPayload
    output_model = TextResult

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            text = bytes.fromhex(payload["text"]).decode("utf-8")
        except ValueError:
            text = ""
        return {"text": text}


class JsonPrettyPlugin(Plugin):
    name = "encoding.json_pretty"
    version = "1.0.0"
    description = "Pretty-prints JSON provided as a string."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raw = payload.get("text", "{}")
        try:
            parsed = json.loads(raw)
            return {"text": json.dumps(parsed, indent=2, sort_keys=True)}
        except json.JSONDecodeError:
            return {"text": raw}


def register_encoding_plugins(registry) -> None:
    registry.register(Base64EncodePlugin(), capabilities=["encoding:base64"])
    registry.register(Base64DecodePlugin(), capabilities=["encoding:base64"])
    registry.register(UrlEncodePlugin(), capabilities=["encoding:url"])
    registry.register(UrlDecodePlugin(), capabilities=["encoding:url"])
    registry.register(HexEncodePlugin(), capabilities=["encoding:hex"])
    registry.register(HexDecodePlugin(), capabilities=["encoding:hex"])
    registry.register(JsonPrettyPlugin(), capabilities=["encoding:json"])
