"""Append-only JSONL trace for safety decisions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.agent.safety import SafetyContext, SafetyDecision

TRACE_NAME = "safety_trace.jsonl"


def append_safety_trace(output_dir: Path, context: SafetyContext, decision: SafetyDecision) -> Path:
    """Append one JSON object to ``outputs/safety_trace.jsonl``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / TRACE_NAME
    payload = {
        "ts": datetime.now(UTC).isoformat(),
        "candidate_action": context.candidate_action,
        "decision": decision.decision,
        "rule_id": decision.rule_id,
        "reasons": decision.reasons,
        "source_artifacts": decision.source_artifacts or context.source_artifacts,
        "mission_id": context.mission_id,
        "run_id": context.run_id,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path

