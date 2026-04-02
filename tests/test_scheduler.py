import asyncio

import pytest

from execution.scheduler import ScheduleOptions, Scheduler


@pytest.mark.asyncio
async def test_scheduler_runs_all_nodes():
    scheduler = Scheduler(ScheduleOptions(concurrency_limit=2))
    stages = [["n1", "n2"], ["n3"]]

    async def runner(node_id: str):
        await asyncio.sleep(0.001)
        return {"node": node_id}

    results = await scheduler.run(stages, runner)
    assert set(results.keys()) == {"n1", "n2", "n3"}
