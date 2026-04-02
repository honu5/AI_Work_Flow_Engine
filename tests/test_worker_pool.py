import asyncio

import pytest

from execution.queue import InMemoryJobQueue
from execution.worker_pool import WorkerPool


@pytest.mark.asyncio
async def test_worker_pool_handles_jobs():
    queue = InMemoryJobQueue()

    async def handler(job):
        await asyncio.sleep(0.001)
        return {"status": "ok", "job_id": job.job_id}

    pool = WorkerPool(queue, handler)
    await pool.start()

    await queue.put("job-1", {"x": 1}, priority=1)
    await queue.put("job-2", {"x": 2}, priority=1)

    await asyncio.sleep(0.02)
    await pool.stop()

    results = pool.results()
    assert results["job-1"]["status"] == "ok"
    assert results["job-2"]["status"] == "ok"
