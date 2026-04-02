from __future__ import annotations

import math
from statistics import mean, median, pstdev
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from plugins.base import Plugin


class ValuesInput(BaseModel):
    values: List[float] = Field(default_factory=list)


class SingleValueOutput(BaseModel):
    value: float


class StatsSummaryOutput(BaseModel):
    count: int
    mean: float
    median: float
    minimum: float
    maximum: float
    stdev: float


class StatsSummaryPlugin(Plugin):
    name = "stats.summary"
    version = "1.0.0"
    description = "Computes descriptive statistics for numeric samples."
    input_model = ValuesInput
    output_model = StatsSummaryOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = list(payload["values"])
        if not values:
            return {"count": 0, "mean": 0.0, "median": 0.0, "minimum": 0.0, "maximum": 0.0, "stdev": 0.0}
        return {
            "count": len(values),
            "mean": float(mean(values)),
            "median": float(median(values)),
            "minimum": float(min(values)),
            "maximum": float(max(values)),
            "stdev": float(pstdev(values)) if len(values) > 1 else 0.0,
        }


class PercentileInput(BaseModel):
    values: List[float]
    percentile: float = Field(ge=0, le=100)


class PercentilePlugin(Plugin):
    name = "stats.percentile"
    version = "1.0.0"
    description = "Linear interpolation percentile."
    input_model = PercentileInput
    output_model = SingleValueOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = sorted(payload["values"])
        if not values:
            return {"value": 0.0}
        k = (len(values) - 1) * (payload["percentile"] / 100.0)
        lower = math.floor(k)
        upper = math.ceil(k)
        if lower == upper:
            return {"value": float(values[int(k)])}
        weight = k - lower
        return {"value": float(values[lower] * (1 - weight) + values[upper] * weight)}


class ZScoreInput(BaseModel):
    values: List[float]
    target: float


class ZScoreOutput(BaseModel):
    z_score: float


class ZScorePlugin(Plugin):
    name = "stats.z_score"
    version = "1.0.0"
    description = "Z-score for a target value against a sample."
    input_model = ZScoreInput
    output_model = ZScoreOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        if len(values) < 2:
            return {"z_score": 0.0}
        avg = mean(values)
        spread = pstdev(values) or 1.0
        return {"z_score": (payload["target"] - avg) / spread}


class HistogramInput(BaseModel):
    values: List[float]
    bins: int = Field(ge=1, le=50)


class HistogramOutput(BaseModel):
    bins: List[Dict[str, float]]


class HistogramPlugin(Plugin):
    name = "stats.histogram"
    version = "1.0.0"
    description = "Builds a fixed-width histogram."
    input_model = HistogramInput
    output_model = HistogramOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        if not values:
            return {"bins": []}
        minimum = min(values)
        maximum = max(values)
        width = (maximum - minimum) / payload["bins"] if maximum != minimum else 1.0
        counts = [0] * payload["bins"]
        for value in values:
            index = min(int((value - minimum) / width), payload["bins"] - 1) if width else 0
            counts[index] += 1
        bins = []
        for index, count in enumerate(counts):
            start = minimum + index * width
            bins.append({"start": start, "end": start + width, "count": float(count)})
        return {"bins": bins}


class MovingAverageInput(BaseModel):
    values: List[float]
    window: int = Field(ge=1)


class MovingAverageOutput(BaseModel):
    values: List[float]


class MovingAveragePlugin(Plugin):
    name = "stats.moving_average"
    version = "1.0.0"
    description = "Simple moving average."
    input_model = MovingAverageInput
    output_model = MovingAverageOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        values = payload["values"]
        window = payload["window"]
        if not values:
            return {"values": []}
        output = []
        for index in range(len(values)):
            start = max(0, index - window + 1)
            chunk = values[start : index + 1]
            output.append(float(mean(chunk)))
        return {"values": output}


class CorrelationInput(BaseModel):
    xs: List[float]
    ys: List[float]


class CorrelationOutput(BaseModel):
    coefficient: float


class CorrelationPlugin(Plugin):
    name = "stats.correlation"
    version = "1.0.0"
    description = "Pearson correlation coefficient."
    input_model = CorrelationInput
    output_model = CorrelationOutput

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        xs = payload["xs"]
        ys = payload["ys"]
        if len(xs) != len(ys) or len(xs) < 2:
            return {"coefficient": 0.0}
        mx, my = mean(xs), mean(ys)
        numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        denom_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
        denom_y = math.sqrt(sum((y - my) ** 2 for y in ys))
        if denom_x == 0 or denom_y == 0:
            return {"coefficient": 0.0}
        return {"coefficient": numerator / (denom_x * denom_y)}


def register_statistics_plugins(registry) -> None:
    registry.register(StatsSummaryPlugin(), capabilities=["stats:summary"])
    registry.register(PercentilePlugin(), capabilities=["stats:percentile"])
    registry.register(ZScorePlugin(), capabilities=["stats:z_score"])
    registry.register(HistogramPlugin(), capabilities=["stats:histogram"])
    registry.register(MovingAveragePlugin(), capabilities=["stats:moving_average"])
    registry.register(CorrelationPlugin(), capabilities=["stats:correlation"])
