from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from pydantic import BaseModel

from plugins.base import Plugin


class ParseIsoInput(BaseModel):
    value: str


class ParseIsoOutput(BaseModel):
    timestamp: str
    year: int
    month: int
    day: int


class ParseIsoPlugin(Plugin):
    name = "datetime.parse_iso"
    version = "1.0.0"
    description = "Parses ISO-8601 timestamps."
    input_model = ParseIsoInput
    output_model = ParseIsoOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dt = datetime.fromisoformat(payload["value"].replace("Z", "+00:00"))
        return {
            "timestamp": dt.isoformat(),
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
        }


class AddDurationInput(BaseModel):
    value: str
    days: int = 0
    hours: int = 0
    minutes: int = 0


class AddDurationOutput(BaseModel):
    timestamp: str


class AddDurationPlugin(Plugin):
    name = "datetime.add_duration"
    version = "1.0.0"
    description = "Adds a duration to an ISO timestamp."
    input_model = AddDurationInput
    output_model = AddDurationOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dt = datetime.fromisoformat(payload["value"].replace("Z", "+00:00"))
        delta = timedelta(days=payload["days"], hours=payload["hours"], minutes=payload["minutes"])
        return {"timestamp": (dt + delta).isoformat()}


class NowUtcPlugin(Plugin):
    name = "datetime.now_utc"
    version = "1.0.0"
    description = "Current UTC timestamp."

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        return {"timestamp": now.isoformat()}


class DiffSecondsInput(BaseModel):
    start: str
    end: str


class DiffSecondsOutput(BaseModel):
    seconds: float


class DiffSecondsPlugin(Plugin):
    name = "datetime.diff_seconds"
    version = "1.0.0"
    description = "Seconds between two ISO timestamps."
    input_model = DiffSecondsInput
    output_model = DiffSecondsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        start = datetime.fromisoformat(payload["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(payload["end"].replace("Z", "+00:00"))
        return {"seconds": (end - start).total_seconds()}


def register_datetime_parse_plugins(registry) -> None:
    registry.register(ParseIsoPlugin(), capabilities=["datetime:parse"])
    registry.register(AddDurationPlugin(), capabilities=["datetime:math"])
    registry.register(NowUtcPlugin(), capabilities=["datetime:now"])
    registry.register(DiffSecondsPlugin(), capabilities=["datetime:diff"])
