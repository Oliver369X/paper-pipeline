"""In-memory run queues for SSE (one stream per POST /run)."""

from __future__ import annotations

import asyncio
from collections import defaultdict

_run_queues: dict[str, asyncio.Queue] = {}
_mission_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


def mission_lock(mid: str) -> asyncio.Lock:
    return _mission_locks[mid]


def register_run(run_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _run_queues[run_id] = q
    return q


def get_queue(run_id: str) -> asyncio.Queue | None:
    return _run_queues.get(run_id)


def forget_run(run_id: str) -> None:
    _run_queues.pop(run_id, None)
