"""Opt-in LangGraph-lite research supervisor."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission

logger = logging.getLogger(__name__)


def _append_trace(out: Path, event: dict) -> None:
    trace_path = out / "research_agent_trace.jsonl"
    line = {"ts": datetime.now(UTC).isoformat(), **event}
    with trace_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")


def run_research_agent_phase(
    mission: Mission,
    client: MistralClient,
    out: Path,
    plog: PipelineLogger,
    *,
    manifest: PipelineManifest | None,
) -> int:
    """Plan sub-tasks when ``research_agent.enabled``. Returns exit code 0 or 1."""

    if not mission.research_agent.enabled:
        return 0

    if manifest:
        manifest.upsert_phase("research_agent", "running")

    plog.step_start("step:research_agent", max_concurrent=mission.research_agent.max_concurrent)
    _append_trace(out, {"event": "supervisor_start", "topic": mission.topic})

    subtasks = mission.sections_needed[: mission.research_agent.max_concurrent]
    prompt = (
        f"Supervisor: decompose research on '{mission.topic}' into {len(subtasks)} sub-tasks.\n"
        f"Sections: {', '.join(subtasks)}\n"
        "Return JSON: {\"subtasks\": [{\"id\": \"t1\", \"goal\": \"...\", \"section\": \"...\"}]}"
    )
    try:
        raw = client.ask_single(prompt, temperature=0.2)
        _append_trace(out, {"event": "supervisor_plan", "raw_len": len(raw)})
    except Exception as exc:
        logger.exception("Research agent supervisor failed")
        plog.step_error("step:research_agent", error="mistral_call_failed", detail=str(exc))
        if manifest:
            manifest.upsert_phase("research_agent", "failed", error=str(exc))
            manifest.write(out)
        return 1

    for i, sec in enumerate(subtasks):
        _append_trace(
            out,
            {
                "event": "subtask_dispatched",
                "index": i,
                "section": sec,
                "status": "planned",
            },
        )

    _append_trace(out, {"event": "supervisor_done", "subtasks": len(subtasks)})
    plog.step_ok("step:research_agent", subtasks=len(subtasks))
    if manifest:
        manifest.upsert_phase("research_agent", "done")
        manifest.write(out)
    return 0
