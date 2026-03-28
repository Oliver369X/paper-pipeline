"""Pure signals from on-disk artifacts for publication eligibility (no network)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission


def compute_publish_signals(output_dir: Path, mission: Mission) -> dict[str, Any]:
    """Combine quality gates + triage tier into a single explainable decision.

    If ``tier == 3`` but quality is not publishable, adds ``tier3_without_quality_gates``.
    """
    qv_path = output_dir / "validation" / "quality_validation.json"
    quality_publishable = False
    quality_reasons: list[str] = []
    if qv_path.is_file():
        try:
            qv = json.loads(qv_path.read_text(encoding="utf-8"))
            quality_publishable = bool(qv.get("publishable"))
            if not quality_publishable:
                quality_reasons.extend(qv.get("blocking_reasons") or ["quality gates"])
        except json.JSONDecodeError:
            quality_reasons.append("invalid quality_validation.json")
    else:
        quality_reasons.append("missing quality_validation.json")

    triage_tier: int | None = None
    triage_label: str | None = None
    tr_path = output_dir / "triage" / "triage_report.json"
    if tr_path.is_file():
        try:
            tr = json.loads(tr_path.read_text(encoding="utf-8"))
            t = tr.get("tier")
            triage_tier = int(t) if t is not None else None
            lab = tr.get("label")
            triage_label = str(lab) if lab is not None else None
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    reasons = list(quality_reasons)
    eligible = quality_publishable and len(reasons) == 0

    if mission.mission_version >= 2 and not mission.enable_quality_check:
        eligible = False
        reasons.append("mission v2 requires quality")

    if triage_tier == 3 and not quality_publishable:
        eligible = False
        reasons.append("tier3_without_quality_gates")

    return {
        "eligible_for_publication": eligible,
        "blocking_reasons": reasons,
        "quality_publishable": quality_publishable,
        "triage_tier": triage_tier,
        "triage_label": triage_label,
        "mission_version": mission.mission_version,
    }
