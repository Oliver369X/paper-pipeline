"""Optional Perplexity quality check on assembled draft."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from perplexity_webui_scraper import Perplexity

from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState
from paper_pipeline.templates import QUALITY_CHECK_TEMPLATE

from .common import build_conversation_config
from .experiment_phase import read_metrics_exit_code

logger = logging.getLogger(__name__)


def run_quality_phase(
    mission: Mission,
    client: Perplexity,
    shared_conversation: Any,
    state: RunState,
    state_path: Path,
    out: Path,
    draft_path: Path,
    plog: PipelineLogger,
    calls_used: int,
    written: list[tuple[str, Path]],
    ctx: dict[str, str],
    *,
    manifest: PipelineManifest | None,
) -> tuple[int, int]:
    """Returns ``(calls_used, exit_code)`` — exit_code 0 or 1."""

    if not (mission.enable_quality_check and calls_used < mission.max_perplexity_calls):
        if manifest:
            manifest.upsert_phase("quality_check", "skipped")
            manifest.write(out)
        return calls_used, 0

    # No reutilizar quality_check de una corrida anterior si el experimento integrado falló (metrics rojo).
    if mission.enable_experiment_runner:
        ec = read_metrics_exit_code(out)
        if ec is not None and ec != 0 and state.already_done("step:quality_check"):
            state.completed_steps = [s for s in state.completed_steps if s != "step:quality_check"]
            state.save(state_path)

    if manifest:
        manifest.upsert_phase("quality_check", "running")

    if state.already_done("step:quality_check"):
        qc_path = out / "quality_gaps.md"
        if qc_path.is_file():
            written.append(("quality_gaps", qc_path))
        plog.step_skip("step:quality_check", reason="already completed in previous run")
        if manifest:
            manifest.upsert_phase("quality_check", "skipped")
            manifest.write(out)
        return calls_used, 0

    draft_body = draft_path.read_text(encoding="utf-8")
    if len(draft_body) > 120_000:
        draft_body = draft_body[:120_000] + "\n\n[truncated for quality check]\n"
    qc_prompt = QUALITY_CHECK_TEMPLATE.format(**ctx, draft=draft_body)
    cfg = build_conversation_config(mission)
    plog.step_start("step:quality_check", model=mission.model)
    _qc_uuid: str | None = None
    try:
        if mission.single_thread_perplexity and shared_conversation is not None:
            conversation = shared_conversation
            logger.info("Perplexity ask: quality_check (same thread as sections)")
        else:
            conversation = client.create_conversation(cfg)
            logger.info("Perplexity ask: quality_check")
        conversation.ask(qc_prompt)
        qc_answer = conversation.answer or ""
        _qc_uuid = getattr(conversation, "uuid", None)
        if _qc_uuid:
            logger.info(
                "Perplexity thread backend_uuid=%s (quality_check; same account as token)",
                _qc_uuid,
            )
        if mission.single_thread_perplexity and _qc_uuid:
            state.perplexity_backend_uuid = _qc_uuid
            state.perplexity_read_write_token = getattr(conversation, "read_write_token", None)
            state.save(state_path)
    except Exception as exc:
        logger.exception("Quality check failed")
        plog.step_error("step:quality_check", error="perplexity_call_failed", detail=str(exc))
        state.errors.append({"step": "quality_check", "detail": str(exc)})
        state.save(state_path)
        if manifest:
            manifest.upsert_phase("quality_check", "failed", error=str(exc))
            manifest.write(out)
        return calls_used, 1

    qc_path = out / "quality_gaps.md"
    qc_path.write_text(
        "<!-- quality_check: assisted review via same Perplexity stack as sections; not independent empirical validation. "
        "See docs/technical/EVALUATION_LAYERS.md -->\n\n"
        f"{qc_answer}\n",
        encoding="utf-8",
    )
    written.append(("quality_gaps", qc_path))
    calls_used += 1

    if mission.enable_experiment_runner:
        ec = read_metrics_exit_code(out)
        if ec is not None and ec != 0:
            plog.step_error(
                "step:quality_check",
                error="experiment_metrics_failed",
                detail=f"metrics exit_code={ec}",
            )
            if manifest:
                manifest.upsert_phase("quality_check", "failed", error="experiment_metrics_failed")
                manifest.write(out)
            return calls_used, 1

    plog.step_ok(
        "step:quality_check",
        chars=len(qc_answer),
        perplexity_backend_uuid=_qc_uuid,
    )
    state.mark_done("step:quality_check")
    state.save(state_path)

    if manifest:
        manifest.upsert_phase("quality_check", "done")
        manifest.write(out)

    return calls_used, 0
