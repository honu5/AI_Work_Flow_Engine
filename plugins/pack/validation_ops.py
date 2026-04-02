from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class RequiredKeysInput(BaseModel):
    data: Dict[str, Any]
    keys: List[str]


class RequiredKeysOutput(BaseModel):
    missing: List[str]


class RequiredKeysPlugin(Plugin):
    name = "validate.required_keys"
    version = "1.0.0"
    description = "Checks for missing required keys."
    input_model = RequiredKeysInput
    output_model = RequiredKeysOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        missing = [key for key in payload["keys"] if key not in payload["data"]]
        return {"missing": missing}


class RangeInput(BaseModel):
    value: float
    minimum: float
    maximum: float


class RangeOutput(BaseModel):
    valid: bool


class RangePlugin(Plugin):
    name = "validate.range"
    version = "1.0.0"
    description = "Validates numeric range."
    input_model = RangeInput
    output_model = RangeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        value = payload["value"]
        return {"valid": payload["minimum"] <= value <= payload["maximum"]}


class LengthInput(BaseModel):
    text: str
    minimum: int = 0
    maximum: int | None = None


class LengthOutput(BaseModel):
    valid: bool


class LengthPlugin(Plugin):
    name = "validate.length"
    version = "1.0.0"
    description = "Validates string length boundaries."
    input_model = LengthInput
    output_model = LengthOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        length = len(payload["text"])
        maximum = payload.get("maximum")
        if maximum is None:
            return {"valid": length >= payload.get("minimum", 0)}
        return {"valid": payload.get("minimum", 0) <= length <= maximum}


class ContainsInput(BaseModel):
    text: str
    needle: str


class ContainsOutput(BaseModel):
    valid: bool


class ContainsPlugin(Plugin):
    name = "validate.contains"
    version = "1.0.0"
    description = "Checks whether text contains a substring."
    input_model = ContainsInput
    output_model = ContainsOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": payload["needle"] in payload["text"]}


class EmailInput(BaseModel):
    value: str


class EmailOutput(BaseModel):
    valid: bool


class EmailPlugin(Plugin):
    name = "validate.email"
    version = "1.0.0"
    description = "Performs a simple email format check."
    input_model = EmailInput
    output_model = EmailOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        value = payload["value"]
        return {"valid": "@" in value and "." in value}


def register_validation_plugins(registry) -> None:
    registry.register(RequiredKeysPlugin(), capabilities=["validate:required"])
    registry.register(RangePlugin(), capabilities=["validate:range"])
    registry.register(LengthPlugin(), capabilities=["validate:length"])
    registry.register(ContainsPlugin(), capabilities=["validate:contains"])
    registry.register(EmailPlugin(), capabilities=["validate:email"])
