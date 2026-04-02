from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, Optional

from execution.queue import InMemoryJobQueue, Job


@dataclass
class WorkerPoolOptions:
    concurrency: int = 4
    poll_interval: float = 0.01


class WorkerPool:
    def __init__(
        self,
        queue: InMemoryJobQueue,
        handler: Callable[[Job], Awaitable[Dict[str, object]]],
        options: Optional[WorkerPoolOptions] = None,
    ) -> None:
        self._queue = queue
        self._handler = handler
        self._options = options or WorkerPoolOptions()
        self._tasks: list[asyncio.Task] = []
        self._running = False
        self._results: Dict[str, Dict[str, object]] = {}

    def results(self) -> Dict[str, Dict[str, object]]:
        return dict(self._results)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        for _ in range(self._options.concurrency):
            self._tasks.append(asyncio.create_task(self._worker()))

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _worker(self) -> None:
        while self._running:
            try:
                job = await self._queue.get()
            except Exception:
                await asyncio.sleep(self._options.poll_interval)
                continue
            if job.cancel_token.cancelled:
                self._results[job.job_id] = {"status": "cancelled"}
                continue
            try:
                result = await self._handler(job)
                self._results[job.job_id] = result
            except Exception as exc:  # noqa: BLE001
                self._results[job.job_id] = {"status": "failed", "error": str(exc)}
