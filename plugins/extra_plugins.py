from __future__ import annotations

from typing import Any, Dict

from plugins.base import Plugin


class TextStatsPlugin(Plugin):
    name = "text_stats"
    version = "1.0.0"
    description = "Computes basic text statistics from a payload."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "") or ""
        words = text.split()
        lines = text.count("\n") + (1 if text else 0)
        return {"chars": len(text), "words": len(words), "lines": lines}


class ReversePlugin(Plugin):
    name = "reverse"
    version = "1.0.0"
    description = "Reverses a string payload."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text", "") or ""
        return {"reversed": text[::-1]}


def register_extra_plugins(registry):
    registry.register(TextStatsPlugin(), capabilities=["text:stats"])
    registry.register(ReversePlugin(), capabilities=["text:reverse"])
