"""Brain (Gemini) chat + apply brief/patch + history + variants."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Query

from paper_pipeline.agent.research_memory import append_research_memory, format_recent_memory_for_brain_prompt
from paper_pipeline.brain.gemini_client import api_key as brain_api_key, brain_sdk_available
from paper_pipeline.brain.perplexity_context import (
    fetch_perplexity_context,
    user_message_requests_arxiv_verification,
)
from paper_pipeline.brain.schemas import (
    BrainApplyRequest,
    BrainChatMessage,
    BrainChatRequest,
    BrainVariantsRequest,
)
from paper_pipeline.brain.service import run_brain_chat, run_brain_variants, trim_brief
from paper_pipeline.brain.settings import (
    brain_max_memory_context_chars,
    brain_max_rag_context_chars,
    brain_default_run_pipeline_on_apply,
    brain_force_perplexity_on_arxiv,
    brain_use_perplexity_context,
)

from ..paths import mission_dir
from .. import storage
from ..run_registry import mission_lock
from .missions_runs import spawn_pipeline_run

router = APIRouter()


def _effective_run_pipeline(body: BrainApplyRequest) -> bool:
    if body.run_pipeline is not None:
        return bool(body.run_pipeline)
    return brain_default_run_pipeline_on_apply()


def _memory_context_for_mission(
    mission_id: str,
    *,
    last_user_message: str | None = None,
) -> str | None:
    out_dir = mission_dir(mission_id) / "outputs"
    max_c = brain_max_memory_context_chars()
    parts: list[str] = []
    if max_c > 0:
        text = format_recent_memory_for_brain_prompt(out_dir, max_chars=max_c)
        if text.strip():
            parts.append(text.strip())
    try:
        from paper_pipeline.rag.settings import rag_enabled_for_brain
        from paper_pipeline.rag.service import rag_context_for_query

        if rag_enabled_for_brain():
            mission_row = storage.read_mission(mission_id)
            pt = getattr(mission_row, "paper_target", "") or ""
            q = f"{(last_user_message or '').strip()}\n{pt}".strip()
            rag_max = brain_max_rag_context_chars()
            if rag_max > 0 and q:
                rag_txt = rag_context_for_query(mission_id, q, max_chars=rag_max)
                if rag_txt and rag_txt.strip():
                    parts.append("### RAG (similitud semántica)\n\n" + rag_txt.strip())
    except Exception:
        pass
    if not parts:
        return None
    return "\n\n".join(parts)


_MAX_CODE_APPLY_CHARS = 200_000


def _write_suggested_code_files(mission_id: str, files: dict[str, str]) -> None:
    """Persist brain-proposed code only under ``outputs/code/`` (path traversal rejected)."""

    if not files:
        return
    root = mission_dir(mission_id).resolve()
    total = 0
    for content in files.values():
        total += len(content)
    if total > _MAX_CODE_APPLY_CHARS:
        raise HTTPException(400, "suggested_code_files exceeds size limit")

    for rel, content in files.items():
        nk = rel.replace("\\", "/").strip().lstrip("/")
        if ".." in nk or nk.startswith("/") or not nk.startswith("outputs/code/"):
            raise HTTPException(400, f"invalid code path (must be under outputs/code/): {rel}")
        target = (root / nk).resolve()
        if not str(target).startswith(str(root)):
            raise HTTPException(400, f"invalid code path: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _apply_brain_storage(mission_id: str, body: BrainApplyRequest, *, tag_apply_run: bool = False) -> None:
    patch_set = body.patch.model_dump(exclude_unset=True)
    if patch_set:
        storage.update_mission(mission_id, body.patch)
    _write_suggested_code_files(mission_id, body.suggested_code_files)
    if body.brief_markdown.strip():
        storage.write_brain_brief(mission_id, body.brief_markdown)
        out_dir = mission_dir(mission_id) / "outputs"
        mission_row = storage.read_mission(mission_id)
        pt = getattr(mission_row, "paper_target", "") or ""
        tags = ["brain", "brief"]
        if tag_apply_run:
            tags.append("apply_and_run")
        append_research_memory(
            out_dir,
            kind="brain_brief",
            summary=body.brief_markdown.strip()[:400],
            source_artifacts=["outputs/brain_brief.md"],
            payload={"mission_id": mission_id, "paper_target": pt},
            tags=tags,
            mission_id=mission_id,
        )
        try:
            from paper_pipeline.rag.service import ingest_brain_brief_only

            ingest_brain_brief_only(out_dir, mission_id)
        except Exception:
            pass


def _last_user_content(messages: list[BrainChatMessage]) -> str:
    for m in reversed(messages):
        if m.role == "user":
            return m.content
    return ""


@router.get("/{mission_id}/brain/history")
def brain_history(
    mission_id: str,
    limit: int = Query(default=200, ge=1, le=2000),
) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    rows = storage.read_brain_chat_history(mission_id, limit=limit)
    messages: list[dict] = []
    for r in rows:
        role = r.get("role")
        if role not in ("user", "assistant"):
            continue
        messages.append(
            {
                "ts": str(r.get("ts") or ""),
                "role": role,
                "content": str(r.get("content") or ""),
            }
        )
    return {"messages": messages}


@router.post("/{mission_id}/brain/export")
def brain_export(mission_id: str) -> dict:
    """Guarda el historial del chat en ``outputs/brain_export_<timestamp>.md`` y ``outputs/brain_latest_export.md``."""

    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    path = storage.write_brain_conversation_export(mission_id)
    rel = path.relative_to(root)
    return {"ok": True, "path": str(rel).replace("\\", "/"), "absolute": str(path.resolve())}


@router.delete("/{mission_id}/brain/history")
def brain_history_delete(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    storage.clear_brain_chat_history(mission_id)
    return {"ok": True}


@router.post("/{mission_id}/brain/chat")
def brain_chat(mission_id: str, body: BrainChatRequest) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    if not brain_api_key():
        raise HTTPException(
            503,
            "Brain disabled: set GOOGLE_API_KEY or GEMINI_API_KEY for Gemini.",
        )
    if not brain_sdk_available():
        raise HTTPException(
            503,
            "Brain disabled: install google-genai in the server environment (pip install google-genai).",
        )
    if not body.messages:
        raise HTTPException(400, "messages must not be empty")
    if body.messages[-1].role != "user":
        raise HTTPException(400, "last message must be from user")

    meta = storage.read_meta(mission_id)
    mission = storage.read_mission(mission_id)
    brief_raw = storage.read_brain_brief(mission_id)
    brief = trim_brief(brief_raw)

    last_u = _last_user_content(body.messages)
    arxiv_ver = user_message_requests_arxiv_verification(last_u)
    use_px = brain_use_perplexity_context() or (
        brain_force_perplexity_on_arxiv() and arxiv_ver
    )
    px: str | None = None
    if use_px:
        px = fetch_perplexity_context(
            topic=mission.topic,
            user_message=last_u,
            paper_target=getattr(mission, "paper_target", "") or "",
            arxiv_verification=arxiv_ver,
        )

    mem_ctx = _memory_context_for_mission(mission_id, last_user_message=last_u)

    out = run_brain_chat(
        body.messages,
        mission=mission,
        meta_title=meta.title,
        meta_description=meta.description,
        persisted_brief=brief,
        memory_context=mem_ctx,
        perplexity_context=px,
    )
    storage.append_brain_chat_turn(
        mission_id,
        user_content=last_u,
        assistant_content=out.reply,
    )
    return out.model_dump()


@router.post("/{mission_id}/brain/variants")
def brain_variants(mission_id: str, body: BrainVariantsRequest) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    if not brain_api_key():
        raise HTTPException(
            503,
            "Brain disabled: set GOOGLE_API_KEY or GEMINI_API_KEY for Gemini.",
        )
    if not brain_sdk_available():
        raise HTTPException(
            503,
            "Brain disabled: install google-genai in the server environment (pip install google-genai).",
        )
    if not body.messages:
        raise HTTPException(400, "messages must not be empty")

    n = body.n
    meta = storage.read_meta(mission_id)
    mission = storage.read_mission(mission_id)
    brief_raw = storage.read_brain_brief(mission_id)
    brief = trim_brief(brief_raw)

    last_uv = _last_user_content(body.messages)
    arxiv_ver_v = user_message_requests_arxiv_verification(last_uv)
    use_px_v = brain_use_perplexity_context() or (
        brain_force_perplexity_on_arxiv() and arxiv_ver_v
    )
    px: str | None = None
    if use_px_v:
        px = fetch_perplexity_context(
            topic=mission.topic,
            user_message=last_uv,
            paper_target=getattr(mission, "paper_target", "") or "",
            arxiv_verification=arxiv_ver_v,
        )

    mem_ctx = _memory_context_for_mission(mission_id, last_user_message=last_uv)

    out = run_brain_variants(
        body.messages,
        n=n,
        mission=mission,
        meta_title=meta.title,
        meta_description=meta.description,
        persisted_brief=brief,
        memory_context=mem_ctx,
        perplexity_context=px,
    )
    return out.model_dump()


@router.post("/{mission_id}/brain/apply")
async def brain_apply(mission_id: str, body: BrainApplyRequest) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")

    run_id: str | None = None
    run = _effective_run_pipeline(body)

    if run:
        async with mission_lock(mission_id):
            _apply_brain_storage(mission_id, body, tag_apply_run=True)
            run_id = spawn_pipeline_run(
                mission_id,
                asyncio.get_running_loop(),
                dry_run=body.dry_run,
            )
    else:
        _apply_brain_storage(mission_id, body, tag_apply_run=False)

    return {"ok": True, "run_id": run_id}


@router.post("/{mission_id}/brain/apply_and_run")
async def brain_apply_and_run(mission_id: str, body: BrainApplyRequest) -> dict:
    """Equivalente a ``POST .../brain/apply`` con ``run_pipeline: true`` (scripts / integraciones)."""

    forced = body.model_copy(update={"run_pipeline": True})
    return await brain_apply(mission_id, forced)
