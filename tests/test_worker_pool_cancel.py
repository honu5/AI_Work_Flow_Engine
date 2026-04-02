import asyncio

import pytest

from execution.queue import InMemoryJobQueue
from execution.worker_pool import WorkerPool


@pytest.mark.asyncio
async def test_worker_pool_handles_cancelled_job():
    queue = InMemoryJobQueue()

    async def handler(job):
        return {"status": "ok"}

    pool = WorkerPool(queue, handler)
    await pool.start()

    job = await queue.put("job-1", {"x": 1}, priority=1)
    job.cancel_token.cancel()

    await asyncio.sleep(0.02)
    await pool.stop()

    results = pool.results()
    assert results["job-1"]["status"] == "cancelled"
