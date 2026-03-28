"""Append-only JSONL trace for objective scoring decisions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.agent.objective_state import ObjectiveState

TRACE_NAME = "objective_trace.jsonl"


def append_objective_trace(
    output_dir: Path,
    state: ObjectiveState,
    *,
    candidate_action_family: str,
) -> Path:
    """Append one JSON object to ``outputs/objective_trace.jsonl``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / TRACE_NAME
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "candidate_action_family": candidate_action_family,
        "utility_total": state.utility_total,
        "terms": state.terms,
        "gates": state.gates,
        "decision_summary": state.status,
        "source_artifacts": state.source_artifacts,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path

