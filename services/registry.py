import asyncio
import time

from config import (
    HOST_MIN_QUERY_INTERVAL_SECONDS,
    HOST_BACKOFF_BASE_SECONDS,
    HOST_BACKOFF_MAX_SECONDS,
)
from services.mcstatus import fetch_server_status, ServerStatus


class HostRegistry:
    def __init__(self):
        self._entries: dict[str, dict] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _normalize(self, host: str) -> str:
        return host.strip().lower()

    def _lock_for(self, host: str) -> asyncio.Lock:
        lock = self._locks.get(host)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[host] = lock
        return lock

    async def get_status(self, host: str, force: bool = False) -> ServerStatus:
        host = self._normalize(host)
        lock = self._lock_for(host)

        async with lock:
            entry = self._entries.get(host)
            now = time.monotonic()

            if not force and entry and now < entry["next_allowed_at"]:
                return entry["status"]

            status = await fetch_server_status(host)

            if status.online:
                next_interval = HOST_MIN_QUERY_INTERVAL_SECONDS
                failures = 0
            else:
                failures = (entry["failures"] + 1) if entry else 1
                next_interval = min(
                    HOST_BACKOFF_BASE_SECONDS * (2 ** (failures - 1)),
                    HOST_BACKOFF_MAX_SECONDS,
                )

            self._entries[host] = {
                "status": status,
                "next_allowed_at": now + next_interval,
                "failures": failures,
            }

            return status


registry = HostRegistry()
