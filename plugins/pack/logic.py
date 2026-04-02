from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class AnyInput(BaseModel):
    values: List[bool]


class AnyOutput(BaseModel):
    result: bool


class AnyPlugin(Plugin):
    name = "logic.any"
    version = "1.0.0"
    description = "Returns True if any value is true."
    input_model = AnyInput
    output_model = AnyOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": any(payload["values"])}


class AllInput(BaseModel):
    values: List[bool]


class AllOutput(BaseModel):
    result: bool


class AllPlugin(Plugin):
    name = "logic.all"
    version = "1.0.0"
    description = "Returns True if all values are true."
    input_model = AllInput
    output_model = AllOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": all(payload["values"])}


class NotInput(BaseModel):
    value: bool


class NotOutput(BaseModel):
    result: bool


class NotPlugin(Plugin):
    name = "logic.not"
    version = "1.0.0"
    description = "Negates a boolean value."
    input_model = NotInput
    output_model = NotOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": not payload["value"]}


class CompareInput(BaseModel):
    left: float
    right: float
    op: str


class CompareOutput(BaseModel):
    result: bool


class ComparePlugin(Plugin):
    name = "logic.compare"
    version = "1.0.0"
    description = "Compares two numbers with an operator."
    input_model = CompareInput
    output_model = CompareOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        op = payload["op"]
        left = payload["left"]
        right = payload["right"]
        mapping = {
            "<": left < right,
            "<=": left <= right,
            ">": left > right,
            ">=": left >= right,
            "==": left == right,
        }
        return {"result": mapping[op]}


class ChooseInput(BaseModel):
    condition: bool
    if_true: Any
    if_false: Any


class ChooseOutput(BaseModel):
    value: Any


class ChoosePlugin(Plugin):
    name = "logic.choose"
    version = "1.0.0"
    description = "Returns one of two values based on a condition."
    input_model = ChooseInput
    output_model = ChooseOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        value = payload["if_true"] if payload["condition"] else payload["if_false"]
        return {"value": value}


def register_logic_plugins(registry) -> None:
    registry.register(AnyPlugin(), capabilities=["logic:any"])
    registry.register(AllPlugin(), capabilities=["logic:all"])
    registry.register(NotPlugin(), capabilities=["logic:not"])
    registry.register(ComparePlugin(), capabilities=["logic:compare"])
    registry.register(ChoosePlugin(), capabilities=["logic:choose"])
