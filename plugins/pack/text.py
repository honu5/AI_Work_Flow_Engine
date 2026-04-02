from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class NormalizeInput(BaseModel):
    text: str
    lowercase: bool = True
    strip: bool = True


class NormalizeOutput(BaseModel):
    text: str


class NormalizeTextPlugin(Plugin):
    name = "text.normalize"
    version = "1.0.0"
    description = "Normalizes text with casing and whitespace rules."
    input_model = NormalizeInput
    output_model = NormalizeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"]
        if payload.get("strip", True):
            text = text.strip()
        if payload.get("lowercase", True):
            text = text.lower()
        return {"text": text}


class TokenizeInput(BaseModel):
    text: str
    pattern: str = Field(default=r"\w+")


class TokenizeOutput(BaseModel):
    tokens: List[str]


class TokenizePlugin(Plugin):
    name = "text.tokenize"
    version = "1.0.0"
    description = "Tokenizes text using a regex pattern."
    input_model = TokenizeInput
    output_model = TokenizeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tokens = re.findall(payload.get("pattern", r"\w+"), payload["text"])
        return {"tokens": tokens}


class CountInput(BaseModel):
    text: str


class CountOutput(BaseModel):
    length: int
    words: int


class CountTextPlugin(Plugin):
    name = "text.count"
    version = "1.0.0"
    description = "Counts characters and words."
    input_model = CountInput
    output_model = CountOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload["text"]
        words = len(re.findall(r"\w+", text))
        return {"length": len(text), "words": words}


class ReplaceInput(BaseModel):
    text: str
    pattern: str
    replacement: str


class ReplaceOutput(BaseModel):
    text: str


class ReplaceTextPlugin(Plugin):
    name = "text.replace"
    version = "1.0.0"
    description = "Replaces text using a regex pattern."
    input_model = ReplaceInput
    output_model = ReplaceOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = re.sub(payload["pattern"], payload["replacement"], payload["text"])
        return {"text": text}


class NgramInput(BaseModel):
    tokens: List[str]
    size: int = 2


class NgramOutput(BaseModel):
    ngrams: List[str]


class NgramPlugin(Plugin):
    name = "text.ngram"
    version = "1.0.0"
    description = "Builds token n-grams."
    input_model = NgramInput
    output_model = NgramOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tokens = payload["tokens"]
        size = payload.get("size", 2)
        ngrams = [" ".join(tokens[i : i + size]) for i in range(len(tokens) - size + 1)]
        return {"ngrams": ngrams}


def register_text_plugins(registry) -> None:
    registry.register(NormalizeTextPlugin(), capabilities=["text:normalize"])
    registry.register(TokenizePlugin(), capabilities=["text:tokenize"])
    registry.register(CountTextPlugin(), capabilities=["text:count"])
    registry.register(ReplaceTextPlugin(), capabilities=["text:replace"])
    registry.register(NgramPlugin(), capabilities=["text:ngram"])
