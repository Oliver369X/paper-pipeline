"""Perplexity section generation loop."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from perplexity_webui_scraper import Perplexity

from paper_pipeline.agent.perplexity_strategy import record_planned_call
from paper_pipeline.events import emit_event
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState
from paper_pipeline.templates import prompt_for_section
from paper_pipeline.validators import validate_section

from .common import build_conversation_config

logger = logging.getLogger(__name__)


def run_perplexity_sections(
    mission: Mission,
    client: Perplexity,
    state: RunState,
    state_path: Path,
    out: Path,
    plog: PipelineLogger,
    calls_used: int,
    written: list[tuple[str, Path]],
    *,
    event_sink: Callable[[dict], None] | None,
    manifest: PipelineManifest | None,
) -> tuple[int, Any, int]:
    """Run the main Perplexity section loop.

    Returns ``(calls_used, shared_conversation, exit_code)`` where *exit_code* is 0 or 1.
    """

    shared_conversation = None
    ctx = {"topic": mission.topic, "paper_target": mission.paper_target}

    if manifest:
        manifest.upsert_phase("perplexity_sections", "running")

    for section in mission.sections_needed:
        if calls_used >= mission.max_perplexity_calls:
            logger.warning(
                "Stopped: max_perplexity_calls=%s reached (skip remaining sections)",
                mission.max_perplexity_calls,
            )
            plog.step_skip(
                f"perplexity:{section}",
                reason="max_perplexity_calls reached",
            )
            break
        step_key = f"perplexity:{section}"
        if state.already_done(step_key):
            target = out / f"{section}.md"
            if target.is_file():
                written.append((section, target))
            plog.step_skip(step_key, reason="already completed in previous run")
            continue
        try:
            prompt = prompt_for_section(section, ctx)
        except KeyError:
            logger.warning("Unknown section key %r, skipping", section)
            plog.step_skip(f"perplexity:{section}", reason="unknown section key")
            continue

        cfg = build_conversation_config(mission)
        plog.step_start(step_key, model=mission.model)
        t0 = time.monotonic()
        emit_event(
            out,
            "section_start",
            {"section": section, "step": step_key},
            sink=event_sink,
        )
        _uuid: str | None = None
        try:
            if mission.single_thread_perplexity:
                if shared_conversation is None:
                    if state.perplexity_backend_uuid:
                        logger.info(
                            "Perplexity resume thread uuid=%s…",
                            state.perplexity_backend_uuid[:8],
                        )
                        shared_conversation = client.resume_conversation(
                            cfg,
                            backend_uuid=state.perplexity_backend_uuid,
                            read_write_token=state.perplexity_read_write_token,
                        )
                    else:
                        shared_conversation = client.create_conversation(cfg)
                conversation = shared_conversation
            else:
                conversation = client.create_conversation(cfg)
            logger.info("Perplexity ask: section=%s", section)
            record_planned_call(
                out,
                prompt=prompt,
                section=section,
                mission_model=mission.model,
                mission_id=None,
            )
            conversation.ask(prompt)
            answer = conversation.answer or ""
            _uuid = getattr(conversation, "uuid", None)
            if _uuid:
                logger.info(
                    "Perplexity thread backend_uuid=%s (session token account; check Library on perplexity.ai)",
                    _uuid,
                )
            if mission.single_thread_perplexity and _uuid:
                state.perplexity_backend_uuid = _uuid
                state.perplexity_read_write_token = getattr(conversation, "read_write_token", None)
                state.save(state_path)
        except Exception as exc:
            logger.exception("Perplexity failed for section=%s", section)
            plog.step_error(step_key, error="perplexity_call_failed", detail=str(exc))
            state.errors.append({"step": step_key, "detail": str(exc)})
            state.save(state_path)
            if manifest:
                manifest.upsert_phase("perplexity_sections", "failed", error=str(exc))
                manifest.write(out)
            return calls_used, shared_conversation, 1

        target = out / f"{section}.md"
        header = (
            f"<!-- section={section} generated={datetime.now(UTC).isoformat()} model={mission.model} -->\n\n"
        )
        target.write_text(header + answer + "\n", encoding="utf-8")
        written.append((section, target))
        calls_used += 1

        vr = validate_section(answer, min_chars=50)
        dur = round(time.monotonic() - t0, 3)
        if not vr.ok:
            plog.step_error(
                step_key,
                error="output_validation_failed",
                detail=vr.reason,
            )
            emit_event(
                out,
                "section_error",
                {"section": section, "detail": vr.reason, "duration_s": dur},
                sink=event_sink,
            )
        else:
            plog.step_ok(
                step_key,
                chars=len(answer),
                perplexity_backend_uuid=_uuid,
            )
            emit_event(
                out,
                "section_done",
                {
                    "section": section,
                    "duration_s": dur,
                    "chars": len(answer),
                },
                sink=event_sink,
            )

        state.mark_done(step_key)
        state.save(state_path)

    if manifest:
        manifest.upsert_phase("perplexity_sections", "done")
        manifest.write(out)

    return calls_used, shared_conversation, 0
