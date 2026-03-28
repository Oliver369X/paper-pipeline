"""Publish eligibility from on-disk artifacts (no network)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from paper_pipeline.agent.safety import SafetyContext, SafetyController
from paper_pipeline.agent.research_memory import append_research_memory
from paper_pipeline.agent.safety_trace import append_safety_trace
from paper_pipeline.mission import Mission

from paper_pipeline.publication.signals import compute_publish_signals


def write_publish_decision(output_dir: Path, mission: Mission) -> Path:
    """Write ``outputs/publication/publish_decision.json``."""

    pub = output_dir / "publication"
    pub.mkdir(parents=True, exist_ok=True)

    signals = compute_publish_signals(output_dir, mission)
    eligible = bool(signals["eligible_for_publication"])
    reasons = list(signals["blocking_reasons"])

    decision: dict[str, Any] = {
        "eligible_for_publication": eligible,
        "blocking_reasons": reasons,
        "mission_version": signals["mission_version"],
        "quality_publishable": signals["quality_publishable"],
        "triage_tier": signals["triage_tier"],
        "triage_label": signals["triage_label"],
    }
    p = pub / "publish_decision.json"
    p.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    metrics_validation_errors: list[str] = []
    triage_path = output_dir / "triage" / "triage_report.json"
    if triage_path.is_file():
        try:
            triage = json.loads(triage_path.read_text(encoding="utf-8"))
            metrics_validation_errors = list(triage.get("metrics_validation_errors") or [])
        except json.JSONDecodeError:
            metrics_validation_errors = []
    ctx = SafetyContext(
        candidate_action="publish_consolidation",
        triage_tier=signals["triage_tier"],
        eligible_for_publication=eligible,
        metrics_validation_errors=metrics_validation_errors,
        publish_blocking_reasons=reasons,
        source_artifacts=[
            "publication/publish_decision.json",
            *(
                ["triage/triage_report.json"]
                if triage_path.is_file()
                else []
            ),
        ],
    )
    append_safety_trace(output_dir, ctx, SafetyController().evaluate(ctx))
    append_research_memory(
        output_dir,
        kind="publish",
        summary=(
            "Publish elegible"
            if eligible
            else "Publish bloqueado o no elegible"
        ),
        source_artifacts=ctx.source_artifacts,
        payload=decision,
        tags=["publish", str(signals["triage_label"] or "unknown")],
        confidence=0.8 if eligible else 0.7,
    )

    if eligible and os.environ.get("PAPER_PIPELINE_BUILD_PACKS", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        try:
            from paper_pipeline.publication.packs import build_code_pack_manifest, build_research_pack

            build_research_pack(output_dir)
            build_code_pack_manifest(output_dir, repo_root=None)
        except OSError:
            pass

    return p
