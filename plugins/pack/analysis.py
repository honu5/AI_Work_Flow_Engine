from __future__ import annotations

from collections import Counter
from math import sqrt
from statistics import mean
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class KeywordDensityInput(BaseModel):
    text: str
    keywords: List[str] = Field(default_factory=list)


class KeywordDensityOutput(BaseModel):
    total_words: int
    matches: Dict[str, int]
    density: Dict[str, float]


class KeywordDensityPlugin(Plugin):
    name = "analysis.keyword_density"
    version = "1.0.0"
    description = "Counts keyword occurrences and calculates their density."
    input_model = KeywordDensityInput
    output_model = KeywordDensityOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        words = [token.lower() for token in payload["text"].split()]
        total_words = len(words)
        counts = Counter(words)
        matches = {keyword: counts.get(keyword.lower(), 0) for keyword in payload.get("keywords", [])}
        density = {
            keyword: (matches[keyword] / total_words if total_words else 0.0)
            for keyword in matches
        }
        return {"total_words": total_words, "matches": matches, "density": density}


class NumericProfileInput(BaseModel):
    values: List[float]


class NumericProfileOutput(BaseModel):
    count: int
    minimum: float
    maximum: float
    average: float
    stdev: float


class NumericProfilePlugin(Plugin):
    name = "analysis.numeric_profile"
    version = "1.0.0"
    description = "Summarizes a numeric sequence."
    input_model = NumericProfileInput
    output_model = NumericProfileOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = list(payload["values"])
        if not values:
            return {"count": 0, "minimum": 0.0, "maximum": 0.0, "average": 0.0, "stdev": 0.0}
        average = mean(values)
        variance = mean([(value - average) ** 2 for value in values]) if len(values) > 1 else 0.0
        return {
            "count": len(values),
            "minimum": min(values),
            "maximum": max(values),
            "average": float(average),
            "stdev": float(sqrt(variance)),
        }


class ChunkInput(BaseModel):
    items: List[Any]
    chunk_size: int = 2


class ChunkOutput(BaseModel):
    chunks: List[List[Any]]


class ChunkListPlugin(Plugin):
    name = "analysis.chunk_list"
    version = "1.0.0"
    description = "Splits a list into equally sized chunks."
    input_model = ChunkInput
    output_model = ChunkOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        items = list(payload["items"])
        chunk_size = max(1, int(payload.get("chunk_size", 2)))
        chunks = [items[index : index + chunk_size] for index in range(0, len(items), chunk_size)]
        return {"chunks": chunks}


class SectionIndexInput(BaseModel):
    text: str


class SectionIndexOutput(BaseModel):
    sections: List[str]


class SectionIndexPlugin(Plugin):
    name = "analysis.section_index"
    version = "1.0.0"
    description = "Extracts markdown-style section headings from text."
    input_model = SectionIndexInput
    output_model = SectionIndexOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sections = []
        for line in payload["text"].splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                sections.append(stripped.lstrip("#").strip())
        return {"sections": sections}


def register_analysis_plugins(registry) -> None:
    registry.register(KeywordDensityPlugin(), capabilities=["analysis:keyword_density"])
    registry.register(NumericProfilePlugin(), capabilities=["analysis:numeric_profile"])
    registry.register(ChunkListPlugin(), capabilities=["analysis:chunk_list"])
    registry.register(SectionIndexPlugin(), capabilities=["analysis:section_index"])
