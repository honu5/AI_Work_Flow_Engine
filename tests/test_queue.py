import asyncio

import pytest

from execution.queue import BackpressureStrategy, InMemoryJobQueue, QueueFullError


@pytest.mark.asyncio
async def test_queue_rejects_when_full():
    queue = InMemoryJobQueue(max_size=1, strategy=BackpressureStrategy.REJECT)
    await queue.put("job-1", {"a": 1}, priority=1)
    with pytest.raises(QueueFullError):
        await queue.put("job-2", {"a": 2}, priority=1)


@pytest.mark.asyncio
async def test_queue_drop_oldest():
    queue = InMemoryJobQueue(max_size=1, strategy=BackpressureStrategy.DROP_OLDEST)
    await queue.put("job-1", {"a": 1}, priority=10)
    await queue.put("job-2", {"a": 2}, priority=1)
    job = await queue.get()
    assert job.job_id == "job-2"


@pytest.mark.asyncio
async def test_queue_priority():
    queue = InMemoryJobQueue()
    await queue.put("job-1", {"a": 1}, priority=5)
    await queue.put("job-2", {"a": 2}, priority=1)
    job = await queue.get()
    assert job.job_id == "job-2"
