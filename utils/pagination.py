from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, TypeVar

T = TypeVar("T")


@dataclass
class Page:
    items: List[T]
    total: int
    offset: int
    limit: int


def paginate(items: Sequence[T], offset: int = 0, limit: int = 50) -> Page[T]:
    total = len(items)
    safe_offset = max(offset, 0)
    safe_limit = max(limit, 1)
    sliced = list(items[safe_offset : safe_offset + safe_limit])
    return Page(items=sliced, total=total, offset=safe_offset, limit=safe_limit)
