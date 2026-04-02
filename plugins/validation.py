from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel


def _get_model(plugin: object, attr: str) -> Optional[Type[BaseModel]]:
    model = getattr(plugin, attr, None)
    if model is None:
        return None
    if not isinstance(model, type) or not issubclass(model, BaseModel):
        raise TypeError(f"{attr} must be a pydantic BaseModel subclass")
    return model


def validate_input(plugin: object, payload: Dict[str, Any]) -> Dict[str, Any]:
    model = _get_model(plugin, "input_model")
    if model is None:
        return payload
    return model(**payload).model_dump()


def validate_output(plugin: object, payload: Dict[str, Any]) -> Dict[str, Any]:
    model = _get_model(plugin, "output_model")
    if model is None:
        return payload
    return model(**payload).model_dump()
