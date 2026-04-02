from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from pydantic import BaseModel

from plugins.base import Plugin


class NowOutput(BaseModel):
    timestamp: str


class NowPlugin(Plugin):
    name = "time.now"
    version = "1.0.0"
    description = "Returns the current UTC timestamp."
    output_model = NowOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"timestamp": datetime.now(timezone.utc).isoformat()}


class ParseInput(BaseModel):
    timestamp: str


class ParseOutput(BaseModel):
    epoch: int


class ParsePlugin(Plugin):
    name = "time.parse"
    version = "1.0.0"
    description = "Parses an ISO timestamp to epoch seconds."
    input_model = ParseInput
    output_model = ParseOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dt = datetime.fromisoformat(payload["timestamp"])
        return {"epoch": int(dt.timestamp())}


class ShiftInput(BaseModel):
    timestamp: str
    seconds: int = 0


class ShiftOutput(BaseModel):
    timestamp: str


class ShiftPlugin(Plugin):
    name = "time.shift"
    version = "1.0.0"
    description = "Shifts a timestamp by a number of seconds."
    input_model = ShiftInput
    output_model = ShiftOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dt = datetime.fromisoformat(payload["timestamp"])
        shifted = dt + timedelta(seconds=payload.get("seconds", 0))
        return {"timestamp": shifted.isoformat()}


class FormatInput(BaseModel):
    timestamp: str
    format: str


class FormatOutput(BaseModel):
    formatted: str


class FormatPlugin(Plugin):
    name = "time.format"
    version = "1.0.0"
    description = "Formats timestamp using a strftime pattern."
    input_model = FormatInput
    output_model = FormatOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dt = datetime.fromisoformat(payload["timestamp"])
        return {"formatted": dt.strftime(payload["format"])}


class WindowInput(BaseModel):
    start: str
    end: str


class WindowOutput(BaseModel):
    seconds: int


class WindowPlugin(Plugin):
    name = "time.window"
    version = "1.0.0"
    description = "Calculates duration between two timestamps."
    input_model = WindowInput
    output_model = WindowOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        start = datetime.fromisoformat(payload["start"])
        end = datetime.fromisoformat(payload["end"])
        return {"seconds": int((end - start).total_seconds())}


def register_time_plugins(registry) -> None:
    registry.register(NowPlugin(), capabilities=["time:now"])
    registry.register(ParsePlugin(), capabilities=["time:parse"])
    registry.register(ShiftPlugin(), capabilities=["time:shift"])
    registry.register(FormatPlugin(), capabilities=["time:format"])
    registry.register(WindowPlugin(), capabilities=["time:window"])
