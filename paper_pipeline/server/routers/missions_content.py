"""Draft, integrated loop, snapshots, directive history."""

from __future__ import annotations

import asyncio
import json
import threading
import uuid

from fastapi import APIRouter, HTTPException

from paper_pipeline.agent.goal_selection import resolve_goal_text
from paper_pipeline.integrated_loop import DEFAULT_GOAL, run_integrated_cycle

from ..paths import mission_dir
from ..run_registry import forget_run, get_queue, mission_lock, register_run
from ..schemas import DraftPut, LoopRequest
from .. import storage

router = APIRouter()


def _async_queue_put(loop: asyncio.AbstractEventLoop, q: asyncio.Queue, item: object) -> None:
    try:
        asyncio.run_coroutine_threadsafe(q.put(item), loop)
    except RuntimeError:
        pass


def _build_cursor_turn(req: LoopRequest) -> str:
    lines: list[str] = []
    if req.perplexity_section:
        lines.append(f"@PERPLEXITY:{req.perplexity_section}")
        if req.perplexity_extra.strip():
            lines.append(req.perplexity_extra.strip())
        lines.append("")
    if req.include_notion:
        lines.append("@NOTION")
        lines.append("")
    if req.cursor_prompt.strip():
        lines.append("@CURSOR")
        lines.append(req.cursor_prompt.strip())
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _loop_thread(
    mission_id: str,
    run_id: str,
    loop: asyncio.AbstractEventLoop,
    *,
    goal: str,
    run_meta: bool,
) -> None:
    q = get_queue(run_id)
    if q is None:
        return
    root = mission_dir(mission_id)
    mission_path = root / "mission.md"
    out = root / "outputs"

    def sink(rec: dict) -> None:
        _async_queue_put(loop, q, rec)

    try:
        storage.read_mission(mission_id)
        draft_before = storage.read_draft(mission_id)
        snap = storage.next_snapshot_path(mission_id)
        if draft_before.strip():
            snap.write_text(draft_before, encoding="utf-8")

        code = run_integrated_cycle(
            mission_path,
            output_dir=out,
            goal=goal,
            run_meta=run_meta,
            event_sink=sink,
        )
        draft_after = storage.read_draft(mission_id)
        storage.append_directive_history(
            mission_id,
            {
                "run_meta": run_meta,
                "exit_code": code,
                "draft_hash_before": len(draft_before),
                "draft_hash_after": len(draft_after),
            },
        )
        _async_queue_put(loop, q, {"event": "loop_finished", "exit_code": code})
    except Exception as exc:
        _async_queue_put(loop, q, {"event": "loop_error", "detail": str(exc)})
    finally:
        _async_queue_put(loop, q, None)


@router.get("/{mission_id}/draft")
def get_draft(mission_id: str) -> dict:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    return {"content": storage.read_draft(mission_id)}


@router.put("/{mission_id}/draft")
def put_draft(mission_id: str, body: DraftPut) -> dict:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    storage.write_draft(mission_id, body.content)
    return {"ok": True}


@router.post("/{mission_id}/loop")
async def start_loop(mission_id: str, req: LoopRequest) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    storage.read_mission(mission_id)
    ct = _build_cursor_turn(req)
    out = root / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    (out / "cursor_turn.md").write_text(ct, encoding="utf-8")
    resolved_goal = resolve_goal_text(out, explicit_goal=req.goal, default_goal=DEFAULT_GOAL)

    async with mission_lock(mission_id):
        run_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        register_run(run_id)
        t = threading.Thread(
            target=_loop_thread,
            args=(mission_id, run_id, loop),
            kwargs={"run_meta": req.run_meta, "goal": resolved_goal},
            daemon=True,
        )
        t.start()
        return {"run_id": run_id}


@router.get("/{mission_id}/snapshots")
def list_snap(mission_id: str) -> dict:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    return {"snapshots": storage.list_snapshots(mission_id)}


@router.get("/{mission_id}/snapshots/{name}")
def get_snap(mission_id: str, name: str) -> dict:
    if not (mission_dir(mission_id) / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    return {"content": storage.read_snapshot(mission_id, name)}


@router.get("/{mission_id}/directive-history")
def directive_hist(mission_id: str) -> list[dict]:
    p = mission_dir(mission_id) / "web" / "directive_history.jsonl"
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
