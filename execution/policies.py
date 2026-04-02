from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0

    @classmethod
    def from_node(cls, node: Dict[str, Any]) -> "RetryPolicy":
        retry = node.get("retry") or {}
        return cls(
            max_attempts=int(retry.get("max_attempts", 1)),
            backoff_seconds=float(retry.get("backoff_seconds", 0.0)),
        )


@dataclass(frozen=True)
class TimeoutPolicy:
    timeout_seconds: Optional[float] = None

    @classmethod
    def from_node(cls, node: Dict[str, Any]) -> "TimeoutPolicy":
        timeout = node.get("timeout_seconds")
        return cls(timeout_seconds=float(timeout) if timeout is not None else None)


@dataclass(frozen=True)
class CachePolicy:
    ttl_seconds: Optional[int] = None
    key_fields: Optional[list[str]] = None

    @classmethod
    def from_node(cls, node: Dict[str, Any]) -> "CachePolicy":
        cache = node.get("cache") or {}
        ttl = cache.get("ttl_seconds")
        fields = cache.get("key_fields")
        return cls(ttl_seconds=int(ttl) if ttl is not None else None, key_fields=fields)
