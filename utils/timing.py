import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timer() -> Iterator[float]:
    start = time.time()
    yield start
