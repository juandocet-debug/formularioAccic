from threading import Lock
from time import monotonic
from typing import Any, Callable


_lock = Lock()
_value: list[dict[str, Any]] | None = None
_expires_at = 0.0


def get_capacity_summary(loader: Callable[[], list[dict[str, Any]]], ttl_seconds: float = 8) -> list[dict[str, Any]]:
    """Keep public capacity reads fast without trusting cached data for registrations."""
    global _value, _expires_at
    now = monotonic()
    with _lock:
        if _value is not None and now < _expires_at:
            return _value

        _value = loader()
        _expires_at = now + ttl_seconds
        return _value


def invalidate_capacity_summary() -> None:
    global _expires_at
    with _lock:
        _expires_at = 0.0
