from __future__ import annotations

import math
from typing import Any, Callable, Dict


def build_default_functions() -> Dict[str, Callable[..., Any]]:
    return {
        "min": min,
        "max": max,
        "abs": abs,
        "round": round,
        "floor": math.floor,
        "ceil": math.ceil,
        "sqrt": math.sqrt,
        "pow": pow,
        "len": len,
        "avg": _avg,
        "clamp": _clamp,
        "between": _between,
        "coalesce": _coalesce,
    }


def _avg(*values: float) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _between(value: float, minimum: float, maximum: float) -> bool:
    return minimum <= value <= maximum


def _coalesce(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None
