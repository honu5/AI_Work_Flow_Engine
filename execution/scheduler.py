from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, Iterable, List


@dataclass
class ScheduleOptions:
    concurrency_limit: int = 4


class Scheduler:
    def __init__(self, options: ScheduleOptions | None = None) -> None:
        self._options = options or ScheduleOptions()

    async def run(
        self,
        stages: Iterable[List[str]],
        runner: Callable[[str], Awaitable[Dict[str, object]]],
    ) -> Dict[str, Dict[str, object]]:
        results: Dict[str, Dict[str, object]] = {}
        semaphore = asyncio.Semaphore(self._options.concurrency_limit)

        async def _run_node(node_id: str) -> None:
            async with semaphore:
                results[node_id] = await runner(node_id)

        for stage in stages:
            tasks = [asyncio.create_task(_run_node(node_id)) for node_id in stage]
            if tasks:
                await asyncio.gather(*tasks)

        return results
