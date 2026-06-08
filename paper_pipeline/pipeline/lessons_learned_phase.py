"""Consolidate research memory into lessons learned."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.common import OPENAI_COMPAT_PROVIDERS
from paper_pipeline.templates import LESSONS_LEARNED_TEMPLATE

logger = logging.getLogger(__name__)


def _read_memory_snippet(out: Path, max_lines: int = 40) -> str:
    mem_path = out / "research_memory.jsonl"
    if not mem_path.is_file():
        return "(no research memory)"
    lines = mem_path.read_text(encoding="utf-8").splitlines()
    tail = lines[-max_lines:]
    return "\n".join(tail) if tail else "(empty memory)"


def run_lessons_learned_phase(
    mission: Mission,
    out: Path,
    plog: PipelineLogger,
    *,
    mistral_client: MistralClient | None = None,
) -> None:
    """Write ``outputs/lessons_learned.md`` when Mistral available."""

    if mission.provider not in OPENAI_COMPAT_PROVIDERS or mistral_client is None:
        plog.step_skip("step:lessons_learned", reason="requires mistral provider")
        return

    quality_path = out / "quality_gaps.md"
    quality = quality_path.read_text(encoding="utf-8") if quality_path.is_file() else "(no quality gaps)"
    memory = _read_memory_snippet(out)

    prompt = LESSONS_LEARNED_TEMPLATE.format(
        topic=mission.topic,
        memory=memory[:20_000],
        quality=quality[:20_000],
    )
    try:
        text = mistral_client.ask_single(prompt, temperature=0.25)
    except Exception as exc:
        logger.warning("Lessons learned generation failed: %s", exc)
        plog.step_error("step:lessons_learned", error="mistral_call_failed", detail=str(exc))
        return

    out_path = out / "lessons_learned.md"
    out_path.write_text(
        f"<!-- lessons_learned: consolidated from research_memory + quality_gaps -->\n\n{text}\n",
        encoding="utf-8",
    )
    plog.step_ok("step:lessons_learned", chars=len(text))
