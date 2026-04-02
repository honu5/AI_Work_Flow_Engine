from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class SwitchInput(BaseModel):
    key: str
    routes: Dict[str, Any]
    default: Any | None = None


class SwitchOutput(BaseModel):
    value: Any


class SwitchPlugin(Plugin):
    name = "route.switch"
    version = "1.0.0"
    description = "Routes to a value based on a key."
    input_model = SwitchInput
    output_model = SwitchOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        routes = payload["routes"]
        value = routes.get(payload["key"], payload.get("default"))
        return {"value": value}


class FanOutInput(BaseModel):
    value: Any
    count: int


class FanOutOutput(BaseModel):
    values: List[Any]


class FanOutPlugin(Plugin):
    name = "route.fanout"
    version = "1.0.0"
    description = "Replicates a value into a list."
    input_model = FanOutInput
    output_model = FanOutOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        count = max(payload["count"], 0)
        return {"values": [payload["value"] for _ in range(count)]}


class GateInput(BaseModel):
    condition: bool
    value: Any


class GateOutput(BaseModel):
    value: Any | None


class GatePlugin(Plugin):
    name = "route.gate"
    version = "1.0.0"
    description = "Passes through a value when condition is true."
    input_model = GateInput
    output_model = GateOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if payload["condition"]:
            return {"value": payload["value"]}
        return {"value": None}


class ThrottleInput(BaseModel):
    values: List[Any]
    every: int


class ThrottleOutput(BaseModel):
    values: List[Any]


class ThrottlePlugin(Plugin):
    name = "route.throttle"
    version = "1.0.0"
    description = "Samples every Nth value."
    input_model = ThrottleInput
    output_model = ThrottleOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        every = max(payload["every"], 1)
        return {"values": payload["values"][::every]}


class MergeInput(BaseModel):
    values: List[Any]


class MergeOutput(BaseModel):
    values: List[Any]


class MergePlugin(Plugin):
    name = "route.merge"
    version = "1.0.0"
    description = "Merges lists into a single list."
    input_model = MergeInput
    output_model = MergeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values: List[Any] = []
        for item in payload["values"]:
            if isinstance(item, list):
                values.extend(item)
            else:
                values.append(item)
        return {"values": values}


def register_routing_plugins(registry) -> None:
    registry.register(SwitchPlugin(), capabilities=["route:switch"])
    registry.register(FanOutPlugin(), capabilities=["route:fanout"])
    registry.register(GatePlugin(), capabilities=["route:gate"])
    registry.register(ThrottlePlugin(), capabilities=["route:throttle"])
    registry.register(MergePlugin(), capabilities=["route:merge"])
