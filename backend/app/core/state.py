"""Application runtime state."""

import time

_startup_time: float = time.time()


def get_uptime_seconds() -> float:
    """Return elapsed seconds since application startup."""
    return round(time.time() - _startup_time, 2)
