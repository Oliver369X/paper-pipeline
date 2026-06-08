"""Optional quality check on assembled draft (Perplexity, MiMo, or Mistral)."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.integrations.xiaomi_mimo import MiMoClient
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.common import OPENAI_COMPAT_PROVIDERS
from paper_pipeline.pipeline.quality_two_phase import (
    quality_rounds_requested,
    run_refutator_round,
    run_two_phase_quality,
    use_two_phase_quality,
)
from paper_pipeline.state import RunState
from paper_pipeline.templates import QUALITY_CHECK_TEMPLATE

from .common import build_conversation_config
from .experiment_phase import read_metrics_exit_code

logger = logging.getLogger(__name__)


def _provider_label(provider: str) -> str:
    if provider == "mistral":
        return "Mistral"
    if provider == "xiaomi_mimo":
        return "MiMo"
    return "Perplexity"


def run_quality_phase(
    mission: Mission,
    client: Any,
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
    mimo_client: MiMoClient | None = None,
    mistral_client: MistralClient | None = None,
) -> tuple[int, int]:
    """Returns ``(calls_used, exit_code)`` — exit_code 0 or 1."""

    if not (mission.enable_quality_check and calls_used < mission.max_perplexity_calls):
        if manifest:
            manifest.upsert_phase("quality_check", "skipped")
            manifest.write(out)
        return calls_used, 0

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
    plog.step_start("step:quality_check", model=mission.model)
    _qc_uuid: str | None = None
    qc_answer = ""
    round1_ok = True

    try:
        if mission.provider == "mistral" and mistral_client is not None:
            if use_two_phase_quality(mission):
                logger.info("Mistral two-phase quality check")
                qc_answer = run_two_phase_quality(mission, mistral_client, draft_body, ctx)
            else:
                truncated = draft_body[:120_000]
                qc_prompt = QUALITY_CHECK_TEMPLATE.format(**ctx, draft=truncated)
                qc_answer = mistral_client.ask_single(qc_prompt, temperature=0.2)
        elif mission.provider == "xiaomi_mimo" and mimo_client is not None:
            logger.info("MiMo ask: quality_check")
            truncated = draft_body[:120_000]
            qc_prompt = QUALITY_CHECK_TEMPLATE.format(**ctx, draft=truncated)
            qc_answer = mimo_client.ask_single(qc_prompt)
        else:
            truncated = draft_body
            if len(truncated) > 120_000:
                truncated = truncated[:120_000] + "\n\n[truncated for quality check]\n"
            qc_prompt = QUALITY_CHECK_TEMPLATE.format(**ctx, draft=truncated)
            cfg = build_conversation_config(mission)
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
        plog.step_error("step:quality_check", error="call_failed", detail=str(exc))
        state.errors.append({"step": "quality_check", "detail": str(exc)})
        state.save(state_path)
        if manifest:
            manifest.upsert_phase("quality_check", "failed", error=str(exc))
            manifest.write(out)
        return calls_used, 1

    provider_note = _provider_label(mission.provider)
    qc_path = out / "quality_gaps.md"
    qc_path.write_text(
        f"<!-- quality_check: assisted review via {provider_note}; not independent empirical validation. "
        "See docs/technical/EVALUATION_LAYERS.md -->\n\n"
        f"{qc_answer}\n",
        encoding="utf-8",
    )
    written.append(("quality_gaps", qc_path))
    calls_used += 1

    if (
        quality_rounds_requested() >= 2
        and mission.provider == "mistral"
        and mistral_client is not None
        and round1_ok
    ):
        try:
            round2 = run_refutator_round(mission, mistral_client, draft_body, ctx)
            (out / "quality_gaps_round2.md").write_text(
                f"<!-- quality_check round 2: refutator -->\n\n{round2}\n",
                encoding="utf-8",
            )
            calls_used += 1
        except Exception as exc:
            logger.warning("Quality round 2 failed: %s", exc)

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
