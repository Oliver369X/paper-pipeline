"""Research plan generation before section LLM calls."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState
from paper_pipeline.templates import RESEARCH_PLAN_TEMPLATE

logger = logging.getLogger(__name__)

_JSON_BLOCK = re.compile(r"\{[\s\S]*\}", re.MULTILINE)


def _parse_plan_json(raw: str) -> dict[str, Any] | None:
    raw = raw.strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK.search(raw)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_plan(data: dict[str, Any], mission: Mission) -> dict[str, Any]:
    sections_out: dict[str, Any] = {}
    raw_sections = data.get("sections")
    if not isinstance(raw_sections, dict):
        raw_sections = {}
    for sec in mission.sections_needed:
        entry = raw_sections.get(sec)
        queries: list[str] = []
        mode = "discovery"
        if isinstance(entry, dict):
            qraw = entry.get("queries")
            if isinstance(qraw, list):
                for q in qraw:
                    if isinstance(q, str) and 20 <= len(q.strip()) <= 500:
                        queries.append(q.strip())
            m = entry.get("mode")
            if isinstance(m, str) and m.strip():
                mode = m.strip()
        if not queries:
            queries = [
                f"Key literature and methods for {sec} on topic: {mission.topic}"[:500],
            ]
        sections_out[sec] = {"queries": queries[:5], "mode": mode}
    return {
        "schema_version": 1,
        "topic": mission.topic,
        "paper_target": mission.paper_target,
        "sections": sections_out,
    }


def run_research_plan_phase(
    mission: Mission,
    client: MistralClient,
    state: RunState,
    state_path: Path,
    out: Path,
    plog: PipelineLogger,
    calls_used: int,
    *,
    manifest: PipelineManifest | None,
) -> tuple[int, int]:
    """Write ``outputs/research_plan.json``. Returns ``(calls_used, exit_code)``."""

    plan_path = out / "research_plan.json"
    if state.already_done("step:research_plan") and plan_path.is_file():
        plog.step_skip("step:research_plan", reason="already completed")
        return calls_used, 0

    if calls_used >= mission.max_perplexity_calls:
        plog.step_skip("step:research_plan", reason="max_llm_calls reached")
        return calls_used, 0

    if manifest:
        manifest.upsert_phase("research_plan", "running")

    sections_list = ", ".join(mission.sections_needed)
    prompt = RESEARCH_PLAN_TEMPLATE.format(
        topic=mission.topic,
        paper_target=mission.paper_target,
        sections=sections_list,
    )

    plog.step_start("step:research_plan", model=mission.model)
    try:
        raw = client.ask_single(prompt, temperature=0.2)
    except Exception as exc:
        logger.exception("Research plan failed")
        plog.step_error("step:research_plan", error="mistral_call_failed", detail=str(exc))
        if manifest:
            manifest.upsert_phase("research_plan", "failed", error=str(exc))
            manifest.write(out)
        return calls_used, 1

    parsed = _parse_plan_json(raw)
    if parsed is None:
        parsed = {"sections": {}}
    plan = _normalize_plan(parsed, mission)
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    calls_used += 1
    state.mark_done("step:research_plan")
    state.save(state_path)
    plog.step_ok("step:research_plan", sections=len(plan.get("sections", {})))
    if manifest:
        manifest.upsert_phase("research_plan", "done")
        manifest.write(out)
    return calls_used, 0
