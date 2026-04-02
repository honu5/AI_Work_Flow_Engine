from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class TextIn(BaseModel):
    text: str


class TextOut(BaseModel):
    text: str


class LinesOutput(BaseModel):
    lines: List[str]


class SplitLinesPlugin(Plugin):
    name = "strings.split_lines"
    version = "1.0.0"
    description = "Splits text into lines."
    input_model = TextIn
    output_model = LinesOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"lines": payload["text"].splitlines()}


class JoinLinesInput(BaseModel):
    lines: List[str]
    separator: str = "\n"


class JoinLinesPlugin(Plugin):
    name = "strings.join_lines"
    version = "1.0.0"
    description = "Joins lines with a separator."
    input_model = JoinLinesInput
    output_model = TextOut

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": payload.get("separator", "\n").join(payload["lines"])}


class RegexFindInput(BaseModel):
    text: str
    pattern: str


class RegexFindOutput(BaseModel):
    matches: List[str]


class RegexFindPlugin(Plugin):
    name = "strings.regex_find"
    version = "1.0.0"
    description = "Returns regex matches."
    input_model = RegexFindInput
    output_model = RegexFindOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        matches = re.findall(payload["pattern"], payload["text"])
        return {"matches": matches}


class RegexReplaceInput(BaseModel):
    text: str
    pattern: str
    replacement: str


class RegexReplacePlugin(Plugin):
    name = "strings.regex_replace"
    version = "1.0.0"
    description = "Regex-based replace."
    input_model = RegexReplaceInput
    output_model = TextOut

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "text": re.sub(payload["pattern"], payload["replacement"], payload["text"]),
        }


class WordCountPlugin(Plugin):
    name = "strings.word_count"
    version = "1.0.0"
    description = "Counts words using regex."
    input_model = TextIn

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        words = re.findall(r"\w+", payload["text"])
        return {"count": len(words), "unique": len(set(words))}


class ExtractNumbersPlugin(Plugin):
    name = "strings.extract_numbers"
    version = "1.0.0"
    description = "Extracts integers and floats from text."
    input_model = TextIn

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        tokens = re.findall(r"-?\d+(?:\.\d+)?", payload["text"])
        numbers = [float(token) if "." in token else int(token) for token in tokens]
        return {"numbers": numbers}


class PrefixSuffixInput(BaseModel):
    text: str
    prefix: str = ""
    suffix: str = ""


class PrefixSuffixPlugin(Plugin):
    name = "strings.affix"
    version = "1.0.0"
    description = "Adds prefix and suffix."
    input_model = PrefixSuffixInput
    output_model = TextOut

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"text": f"{payload.get('prefix', '')}{payload['text']}{payload.get('suffix', '')}"}


class TruncateWordsInput(BaseModel):
    text: str
    max_words: int = Field(ge=1)


class TruncateWordsPlugin(Plugin):
    name = "strings.truncate_words"
    version = "1.0.0"
    description = "Truncates after N words."
    input_model = TruncateWordsInput
    output_model = TextOut

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        words = payload["text"].split()
        trimmed = " ".join(words[: payload["max_words"]])
        return {"text": trimmed}


def register_string_plugins(registry) -> None:
    registry.register(SplitLinesPlugin(), capabilities=["strings:split"])
    registry.register(JoinLinesPlugin(), capabilities=["strings:join"])
    registry.register(RegexFindPlugin(), capabilities=["strings:regex"])
    registry.register(RegexReplacePlugin(), capabilities=["strings:regex"])
    registry.register(WordCountPlugin(), capabilities=["strings:count"])
    registry.register(ExtractNumbersPlugin(), capabilities=["strings:numbers"])
    registry.register(PrefixSuffixPlugin(), capabilities=["strings:affix"])
    registry.register(TruncateWordsPlugin(), capabilities=["strings:truncate"])
