
from contextlib import contextmanager
import time
from typing import Iterator, List

@contextmanager
def timer() -> Iterator[List[float]]:
    """Context manager that yields (start, end) timestamps."""
    t = [time.perf_counter()]   # mutable list
    yield t
    t.append(time.perf_counter())