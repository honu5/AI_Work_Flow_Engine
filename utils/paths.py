from __future__ import annotations

from typing import Any, Iterable, List


class PathResolutionError(KeyError):
    pass


def normalize_path(path: str | Iterable[str]) -> List[str]:
    if isinstance(path, str):
        return [segment for segment in path.split(".") if segment]
    return list(path)


def get_in(data: Any, path: str | Iterable[str], default: Any = None) -> Any:
    current = data
    for segment in normalize_path(path):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        else:
            return default
    return current


def require_in(data: Any, path: str | Iterable[str]) -> Any:
    current = data
    for segment in normalize_path(path):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        else:
            raise PathResolutionError(f"Missing required path segment: {segment}")
    return current
