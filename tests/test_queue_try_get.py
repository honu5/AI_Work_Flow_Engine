import pytest

from execution.queue import InMemoryJobQueue, QueueEmptyError


def test_queue_try_get_empty():
    queue = InMemoryJobQueue()
    with pytest.raises(QueueEmptyError):
        queue.try_get()
