"""Two-phase quality review (ChatReviewer-style)."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.mission import Mission
from paper_pipeline.templates import (
    QUALITY_STAGE1_TEMPLATE,
    QUALITY_STAGE2_TEMPLATE,
    QUALITY_REFUTATOR_TEMPLATE,
)

logger = logging.getLogger(__name__)

_JSON_OBJ = re.compile(r"\{[\s\S]*\}", re.MULTILINE)
_REQUIRED_H2 = ("## Strengths", "## Weaknesses", "## Missing citations", "## Suggestions")


def parse_stage1_sections(raw: str, available: list[str]) -> list[str]:
    raw = raw.strip()
    data: dict[str, Any] | None = None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            data = parsed
    except json.JSONDecodeError:
        match = _JSON_OBJ.search(raw)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    data = parsed
            except json.JSONDecodeError:
                pass
    chosen: list[str] = []
    if data:
        sec = data.get("sections")
        if isinstance(sec, list):
            for s in sec:
                if isinstance(s, str) and s in available and s not in chosen:
                    chosen.append(s)
    if len(chosen) < 2 and available:
        for fallback in available:
            if fallback not in chosen:
                chosen.append(fallback)
            if len(chosen) >= 2:
                break
    return chosen[:2]


def run_two_phase_quality(
    mission: Mission,
    client: MistralClient,
    draft_body: str,
    ctx: dict[str, str],
) -> str:
    """Return structured quality review markdown."""
    excerpt = draft_body[:8000]
    sections = [s for s in mission.sections_needed if s != "peer_review"]
    stage1_prompt = QUALITY_STAGE1_TEMPLATE.format(
        topic=ctx.get("topic", mission.topic),
        draft_excerpt=excerpt,
        sections=", ".join(sections) or "related_work, methodology",
    )
    stage1_raw = client.ask_single(stage1_prompt, temperature=0.1)
    focus = parse_stage1_sections(stage1_raw, sections or mission.sections_needed)

    truncated = draft_body
    if len(truncated) > 120_000:
        truncated = truncated[:120_000] + "\n\n[truncated for quality check]\n"

    stage2_prompt = QUALITY_STAGE2_TEMPLATE.format(
        topic=ctx.get("topic", mission.topic),
        paper_target=ctx.get("paper_target", mission.paper_target),
        focus_sections=", ".join(focus),
        draft=truncated,
    )
    review = client.ask_single(stage2_prompt, temperature=0.2)
    for heading in _REQUIRED_H2:
        if heading not in review:
            review += f"\n\n{heading}\n\n_(Section missing from model output; add manually.)_\n"
    header = (
        f"<!-- quality_check: two-phase Mistral review; focus={','.join(focus)} -->\n\n"
        f"## Focus sections\n{', '.join(focus)}\n\n"
    )
    return header + review


def run_refutator_round(
    mission: Mission,
    client: MistralClient,
    draft_body: str,
    ctx: dict[str, str],
) -> str:
    truncated = draft_body
    if len(truncated) > 120_000:
        truncated = truncated[:120_000] + "\n\n[truncated]\n"
    prompt = QUALITY_REFUTATOR_TEMPLATE.format(
        topic=ctx.get("topic", mission.topic),
        draft=truncated,
    )
    return client.ask_single(prompt, temperature=0.15)


def quality_rounds_requested() -> int:
    raw = os.environ.get("PAPER_PIPELINE_QUALITY_ROUNDS", "1").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 1
    return max(1, min(n, 2))


def use_two_phase_quality(mission: Mission) -> bool:
    if mission.provider == "mistral":
        return True
    flag = os.environ.get("PAPER_PIPELINE_QUALITY_2PHASE", "").strip().lower()
    return flag in ("1", "true", "yes")
