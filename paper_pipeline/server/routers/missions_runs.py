"""Pipeline runs, SSE, logs, run state, pipeline events."""

from __future__ import annotations

import asyncio
import json
import threading
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from paper_pipeline.orchestrator_v2 import run_pipeline_v2

from ..paths import mission_dir
from ..run_registry import forget_run, get_queue, mission_lock, register_run
from .. import storage

router = APIRouter()


def _async_queue_put(loop: asyncio.AbstractEventLoop, q: asyncio.Queue, item: object) -> None:
    """Encola en el loop principal; ignora si el loop ya se cerró (p. ej. tests)."""
    try:
        asyncio.run_coroutine_threadsafe(q.put(item), loop)
    except RuntimeError:
        pass


def _run_pipeline_thread(
    mission_id: str,
    run_id: str,
    loop: asyncio.AbstractEventLoop,
    *,
    dry_run: bool,
) -> None:
    q = get_queue(run_id)
    if q is None:
        return
    mission_path = mission_dir(mission_id) / "mission.md"

    def sink(rec: dict) -> None:
        _async_queue_put(loop, q, rec)

    try:
        code = run_pipeline_v2(mission_path, dry_run=dry_run, event_sink=sink)
        _async_queue_put(loop, q, {"event": "run_finished", "exit_code": code})
    except Exception as exc:
        _async_queue_put(loop, q, {"event": "run_error", "detail": str(exc)})
    finally:
        _async_queue_put(loop, q, None)


def spawn_pipeline_run(
    mission_id: str,
    loop: asyncio.AbstractEventLoop,
    *,
    dry_run: bool = False,
) -> str:
    """Register SSE queue, start ``run_pipeline_v2`` in a daemon thread. Caller must hold ``mission_lock`` if required."""

    run_id = uuid.uuid4().hex
    register_run(run_id)
    t = threading.Thread(
        target=_run_pipeline_thread,
        args=(mission_id, run_id, loop),
        kwargs={"dry_run": dry_run},
        daemon=True,
    )
    t.start()
    return run_id


@router.post("/{mission_id}/run")
async def start_pipeline(mission_id: str, dry_run: bool = False) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    async with mission_lock(mission_id):
        run_id = spawn_pipeline_run(mission_id, asyncio.get_running_loop(), dry_run=dry_run)
        return {"run_id": run_id}


@router.get("/{mission_id}/events/{run_id}")
async def stream_events(mission_id: str, run_id: str):
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    q = get_queue(run_id)
    if q is None:
        raise HTTPException(404, "Unknown run_id")

    async def gen():
        try:
            while True:
                item = await q.get()
                if item is None:
                    yield "data: " + json.dumps({"event": "stream_end"}) + "\n\n"
                    break
                yield "data: " + json.dumps(item, ensure_ascii=False) + "\n\n"
        finally:
            forget_run(run_id)

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/{mission_id}/run-log")
def get_run_log(mission_id: str) -> list[dict]:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    return storage.read_run_log_lines(mission_id)


@router.get("/{mission_id}/events-log")
def get_pipeline_events_log(mission_id: str) -> list[dict]:
    """Eventos estructurados de ``outputs/pipeline_events.jsonl`` (timeline del pipeline)."""

    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    return storage.read_pipeline_events(mission_id)


@router.get("/{mission_id}/run-state")
def get_run_state(mission_id: str) -> dict:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    st = storage.read_run_state(mission_id)
    if st is None:
        return {}
    return st
