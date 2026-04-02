import pytest

from execution.queue import InMemoryJobQueue


@pytest.mark.asyncio
async def test_queue_cancel_marks_job():
    queue = InMemoryJobQueue()
    job = await queue.put("job-1", {"x": 1}, priority=1)
    assert queue.cancel("job-1") is True
    assert job.cancel_token.cancelled is True
