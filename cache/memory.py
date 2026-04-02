from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

from cache.base import CacheBackend


class InMemoryCache(CacheBackend):
    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Optional[float], Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        record = self._store.get(key)
        if record is None:
            return None
        expires_at, value = record
        if expires_at is not None and time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        expires_at = None
        if ttl_seconds is not None:
            expires_at = time.time() + ttl_seconds
        self._store[key] = (expires_at, value)

    def invalidate(self, key_prefix: str) -> int:
        keys = [key for key in self._store if key.startswith(key_prefix)]
        for key in keys:
            self._store.pop(key, None)
        return len(keys)
