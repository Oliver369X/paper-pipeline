"""Notion sync v2 — editorial projection from on-disk truth (ledger/evidence).

The canonical state remains under ``outputs/``; Notion receives summaries only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission


def build_notion_payload_from_outputs(
    mission: Mission,
    output_dir: Path,
    *,
    run_id: str = "",
) -> dict[str, Any]:
    """Construct a JSON payload suitable for REST sync (no MCP in Python)."""

    ledger_path = output_dir / "run_ledger.json"
    triage_path = output_dir / "triage" / "triage_report.json"
    pub_path = output_dir / "publication" / "publish_decision.json"

    payload: dict[str, Any] = {
        "mission_id": output_dir.parent.name,
        "run_id": run_id,
        "topic": mission.topic,
        "paper_target": mission.paper_target,
        "has_ledger": ledger_path.is_file(),
        "has_triage": triage_path.is_file(),
        "has_publish_decision": pub_path.is_file(),
    }
    return payload
