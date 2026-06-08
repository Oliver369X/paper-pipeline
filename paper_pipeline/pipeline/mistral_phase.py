"""Mistral section generation loop."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.events import emit_event
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState
from paper_pipeline.templates import prompt_for_section
from paper_pipeline.validators import validate_section

logger = logging.getLogger(__name__)


def _plan_context(out: Path, section: str) -> str:
    plan_path = out / "research_plan.json"
    if not plan_path.is_file():
        return ""
    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    sections = data.get("sections") if isinstance(data, dict) else None
    if not isinstance(sections, dict):
        return ""
    entry = sections.get(section)
    if not isinstance(entry, dict):
        return ""
    queries = entry.get("queries")
    if not isinstance(queries, list) or not queries:
        return ""
    lines = ["Research plan queries for this section:"]
    for q in queries[:5]:
        if isinstance(q, str) and q.strip():
            lines.append(f"- {q.strip()}")
    return "\n".join(lines) + "\n\n"


def run_mistral_sections(
    mission: Mission,
    client: MistralClient,
    state: RunState,
    state_path: Path,
    out: Path,
    plog: PipelineLogger,
    calls_used: int,
    written: list[tuple[str, Path]],
    *,
    event_sink: Callable[[dict], None] | None,
    manifest: PipelineManifest | None,
) -> tuple[int, int]:
    """Run the main Mistral section loop. Returns ``(calls_used, exit_code)``."""

    ctx = {"topic": mission.topic, "paper_target": mission.paper_target}

    if manifest:
        manifest.upsert_phase("mistral_sections", "running")

    for section in mission.sections_needed:
        if calls_used >= mission.max_perplexity_calls:
            logger.warning(
                "Stopped: max_perplexity_calls=%s reached (skip remaining sections)",
                mission.max_perplexity_calls,
            )
            plog.step_skip(
                f"mistral:{section}",
                reason="max_perplexity_calls reached",
            )
            break
        step_key = f"mistral:{section}"
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
            plog.step_skip(f"mistral:{section}", reason="unknown section key")
            continue

        plan_ctx = _plan_context(out, section)
        full_prompt = plan_ctx + prompt if plan_ctx else prompt

        plog.step_start(step_key, model=mission.model)
        t0 = time.monotonic()
        emit_event(
            out,
            "section_start",
            {"section": section, "step": step_key},
            sink=event_sink,
        )
        try:
            conversation = client.create_conversation()
            logger.info("Mistral ask: section=%s", section)
            answer = conversation.ask(full_prompt)
            conversation.close()
        except Exception as exc:
            logger.exception("Mistral failed for section=%s", section)
            plog.step_error(step_key, error="mistral_call_failed", detail=str(exc))
            state.errors.append({"step": step_key, "detail": str(exc)})
            state.save(state_path)
            if manifest:
                manifest.upsert_phase("mistral_sections", "failed", error=str(exc))
                manifest.write(out)
            return calls_used, 1

        target = out / f"{section}.md"
        header = (
            f"<!-- section={section} generated={datetime.now(UTC).isoformat()} "
            f"model={mission.model} provider=mistral -->\n\n"
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
        manifest.upsert_phase("mistral_sections", "done")
        manifest.write(out)

    return calls_used, 0
