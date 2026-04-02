from __future__ import annotations

import asyncio
from typing import Any, Dict

from plugins.base import Plugin
from plugins.registry import PluginRegistry


class EchoPlugin(Plugin):
    name = "echo"
    version = "1.0.0"
    description = "Echoes the input payload."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = dict(payload.get("input", {}))
        node = payload.get("node") or {}
        merged.update(node.get("input") or {})
        return {"echo": {"input": merged}}


class AddNumbersPlugin(Plugin):
    name = "add_numbers"
    version = "1.0.0"
    description = "Adds two numbers from the payload."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        return {"sum": a + b}


class SleepPlugin(Plugin):
    name = "sleep"
    version = "1.0.0"
    description = "Sleeps for the given seconds and returns the elapsed time."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        seconds = float(payload.get("seconds", 0.01))
        await asyncio.sleep(seconds)
        return {"slept": seconds}


def register_builtin_plugins(registry: PluginRegistry) -> None:
    registry.register(EchoPlugin(), capabilities=["core:echo"])
    registry.register(AddNumbersPlugin(), capabilities=["math:add"])
    registry.register(SleepPlugin(), capabilities=["time:sleep"])
