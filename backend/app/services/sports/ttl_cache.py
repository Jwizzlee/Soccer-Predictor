"""In-memory TTL cache for API-Football responses (process-local, no Redis)."""

from __future__ import annotations

import time
from threading import Lock
from typing import Any

# Player search + league-scoped fixture lists: 1 hour
SEARCH_AND_LEAGUE_TTL_SECONDS = 60 * 60
# Completed match player stats: 12 hours
FIXTURE_PLAYERS_TTL_SECONDS = 12 * 60 * 60


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[tuple[Any, ...], tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: tuple[Any, ...]) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() >= expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: tuple[Any, ...], value: Any, ttl_seconds: float) -> None:
        with self._lock:
            self._store[key] = (value, time.monotonic() + ttl_seconds)


# Shared across all ApiFootballClient instances in this process.
api_football_cache = TTLCache()
