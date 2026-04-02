from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel

from plugins.base import Plugin


class SumInput(BaseModel):
    values: List[float]


class SumOutput(BaseModel):
    total: float


class SumPlugin(Plugin):
    name = "math.sum"
    version = "1.0.0"
    description = "Sums numeric values."
    input_model = SumInput
    output_model = SumOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"total": float(sum(payload["values"]))}


class AverageInput(BaseModel):
    values: List[float]


class AverageOutput(BaseModel):
    average: float


class AveragePlugin(Plugin):
    name = "math.average"
    version = "1.0.0"
    description = "Calculates average of values."
    input_model = AverageInput
    output_model = AverageOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        if not values:
            return {"average": 0.0}
        return {"average": float(sum(values)) / len(values)}


class MultiplyInput(BaseModel):
    values: List[float]


class MultiplyOutput(BaseModel):
    product: float


class MultiplyPlugin(Plugin):
    name = "math.multiply"
    version = "1.0.0"
    description = "Multiplies numeric values."
    input_model = MultiplyInput
    output_model = MultiplyOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        product = 1.0
        for value in payload["values"]:
            product *= value
        return {"product": product}


class ClampInput(BaseModel):
    value: float
    minimum: float
    maximum: float


class ClampOutput(BaseModel):
    value: float


class ClampPlugin(Plugin):
    name = "math.clamp"
    version = "1.0.0"
    description = "Clamps value between min and max."
    input_model = ClampInput
    output_model = ClampOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        value = payload["value"]
        minimum = payload["minimum"]
        maximum = payload["maximum"]
        return {"value": max(minimum, min(maximum, value))}


class NormalizeInput(BaseModel):
    value: float
    minimum: float
    maximum: float


class NormalizeOutput(BaseModel):
    normalized: float


class NormalizePlugin(Plugin):
    name = "math.normalize"
    version = "1.0.0"
    description = "Normalizes a value between 0 and 1."
    input_model = NormalizeInput
    output_model = NormalizeOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        minimum = payload["minimum"]
        maximum = payload["maximum"]
        if maximum == minimum:
            return {"normalized": 0.0}
        return {"normalized": (payload["value"] - minimum) / (maximum - minimum)}


def register_math_plugins(registry) -> None:
    registry.register(SumPlugin(), capabilities=["math:sum"])
    registry.register(AveragePlugin(), capabilities=["math:average"])
    registry.register(MultiplyPlugin(), capabilities=["math:multiply"])
    registry.register(ClampPlugin(), capabilities=["math:clamp"])
    registry.register(NormalizePlugin(), capabilities=["math:normalize"])
