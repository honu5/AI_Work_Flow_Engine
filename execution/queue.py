from __future__ import annotations

import asyncio
import heapq
import itertools
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


class QueueFullError(RuntimeError):
    pass


class QueueEmptyError(RuntimeError):
    pass


@dataclass
class CancelToken:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


@dataclass(order=True)
class Job:
    priority: int
    sequence: int = field(compare=True)
    job_id: str = field(compare=False, default="")
    payload: Dict[str, Any] = field(compare=False, default_factory=dict)
    created_at: str = field(compare=False, default_factory=lambda: datetime.utcnow().isoformat())
    cancel_token: CancelToken = field(compare=False, default_factory=CancelToken)


class BackpressureStrategy:
    BLOCK = "block"
    REJECT = "reject"
    DROP_OLDEST = "drop_oldest"


class InMemoryJobQueue:
    def __init__(self, max_size: int = 1000, strategy: str = BackpressureStrategy.BLOCK) -> None:
        self._max_size = max_size
        self._strategy = strategy
        self._counter = itertools.count()
        self._jobs: List[Job] = []
        self._cond = asyncio.Condition()

    def size(self) -> int:
        return len(self._jobs)

    async def put(self, job_id: str, payload: Dict[str, Any], priority: int = 100) -> Job:
        async with self._cond:
            if self._max_size and len(self._jobs) >= self._max_size:
                if self._strategy == BackpressureStrategy.REJECT:
                    raise QueueFullError("Queue is full")
                if self._strategy == BackpressureStrategy.DROP_OLDEST:
                    self._drop_lowest_priority()
                else:
                    while self._max_size and len(self._jobs) >= self._max_size:
                        await self._cond.wait()
            job = Job(priority=priority, sequence=next(self._counter), job_id=job_id, payload=payload)
            heapq.heappush(self._jobs, job)
            self._cond.notify_all()
            return job

    async def get(self) -> Job:
        async with self._cond:
            while not self._jobs:
                await self._cond.wait()
            job = heapq.heappop(self._jobs)
            self._cond.notify_all()
            return job

    def try_get(self) -> Job:
        if not self._jobs:
            raise QueueEmptyError("Queue is empty")
        job = heapq.heappop(self._jobs)
        return job

    def cancel(self, job_id: str) -> bool:
        for job in self._jobs:
            if job.job_id == job_id:
                job.cancel_token.cancel()
                return True
        return False

    def _drop_lowest_priority(self) -> None:
        if not self._jobs:
            return
        worst = max(self._jobs)
        self._jobs.remove(worst)
        heapq.heapify(self._jobs)
