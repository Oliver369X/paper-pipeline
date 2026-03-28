"""Structural and epistemic quality gates (machine-readable report)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.experiment_contracts import TIER_FULL_EMPIRICAL, infer_replication_tier
from paper_pipeline.validation.claim_extractor import extract_claims_from_draft

_RISKY_REPLICATION = re.compile(
    r"(faithful\s+replication|réplica\s+fiel|reproducimos\s+el\s+paper|full\s+replication\s+of\s+the\s+paper)",
    re.I,
)
_DOWNSTREAM_KW = (
    "reasoning",
    "arithmetic",
    "factual",
    "perplexity",
    "loose",
    "strict",
    "levenshtein",
)


def _read_metrics(output_dir: Path) -> dict[str, Any] | None:
    p = output_dir / "metrics.json"
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def run_quality_gates(mission: Mission, output_dir: Path) -> tuple[bool, dict[str, Any]]:
    """Run gates; return (all_passed, report dict)."""

    gates: list[dict[str, Any]] = []
    blocking: list[str] = []
    warnings: list[str] = []

    draft = output_dir / "draft_paper.md"
    draft_body = ""
    if draft.is_file():
        draft_body = draft.read_text(encoding="utf-8")

    if not draft.is_file():
        gates.append({"id": "structural_draft", "passed": False, "detail": "draft_paper.md missing"})
        blocking.append("missing draft")
    else:
        wc = len(draft_body.split())
        ok = wc >= 5
        gates.append(
            {
                "id": "structural_draft",
                "passed": ok,
                "detail": f"word_count={wc}",
            }
        )
        if not ok:
            blocking.append("draft too short")

    # Section outputs (best-effort)
    missing_sections: list[str] = []
    for sec in mission.sections_needed:
        p = output_dir / f"{sec}.md"
        if not p.is_file():
            missing_sections.append(sec)
    sec_ok = len(missing_sections) == 0
    gates.append(
        {
            "id": "structural_sections",
            "passed": sec_ok,
            "detail": {"missing": missing_sections} if missing_sections else "ok",
        }
    )
    if not sec_ok:
        blocking.append("missing section files")

    claims: list[dict[str, Any]] = []
    if draft.is_file():
        claims = extract_claims_from_draft(draft)
    gates.append(
        {
            "id": "epistemic_claim_candidates",
            "passed": True,
            "detail": f"claim_candidates={len(claims)}",
        }
    )

    metrics = _read_metrics(output_dir)
    qg = mission.quality_gates
    align_mode = (qg.epistemic_alignment_mode or "off").strip().lower()
    if align_mode not in ("off", "warn", "block"):
        align_mode = "off"

    tier = "unknown"
    if metrics:
        tier = str(metrics.get("replication_tier") or infer_replication_tier(metrics))

    epistemic_passed = True
    epistemic_detail: dict[str, Any] = {"replication_tier": tier, "mode": align_mode}
    if align_mode != "off" and draft_body and tier and tier != TIER_FULL_EMPIRICAL:
        if _RISKY_REPLICATION.search(draft_body):
            epistemic_passed = False
            epistemic_detail["risky_replication_language"] = True
            if align_mode == "block":
                blocking.append("epistemic_alignment: lenguaje de réplica fiel sin tier full_empirical")
            else:
                warnings.append("epistemic_alignment: posible sobreclaim de réplica (warn)")

    gates.append(
        {
            "id": "epistemic_alignment",
            "passed": epistemic_passed,
            "detail": epistemic_detail,
        }
    )

    fallback_passed = True
    fb_detail: dict[str, Any] = {"mode": align_mode}
    metrics_er = metrics.get("experiment_runner") if metrics else None
    metrics_er = metrics_er if isinstance(metrics_er, dict) else {}
    if metrics and metrics_er.get("fallback_from_hf_import") is True:
        rs = output_dir / "replication_status.md"
        has_rs = rs.is_file()
        mentions = "DEGRADED" in draft_body or "partial infrastructure" in draft_body.lower()
        fallback_passed = has_rs or mentions
        fb_detail = {
            "fallback_from_hf_import": True,
            "has_replication_status_md": has_rs,
            "draft_mentions_degraded": mentions,
        }
        if not fallback_passed:
            if align_mode == "block":
                blocking.append("fallback_transparency: falta replication_status.md o aviso en borrador")
            elif align_mode == "warn":
                warnings.append("fallback_transparency: documentar fallback HF→numpy")

    gates.append(
        {
            "id": "fallback_transparency",
            "passed": fallback_passed,
            "detail": fb_detail,
        }
    )

    downstream_mode = (qg.downstream_metrics_mode or "off").strip().lower()
    if downstream_mode not in ("off", "warn", "block"):
        downstream_mode = "off"

    downstream_passed = True
    low = draft_body.lower()
    hits = sum(1 for k in _DOWNSTREAM_KW if k in low)
    downstream_detail: dict[str, Any] = {
        "keyword_hits": hits,
        "replication_fidelity": mission.replication_fidelity or "",
        "mode": downstream_mode,
    }
    if (
        downstream_mode != "off"
        and (mission.replication_fidelity or "").strip().lower() == "strict_paper"
        and draft_body
    ):
        if hits < 3:
            downstream_passed = False
            if downstream_mode == "block":
                blocking.append("downstream_metrics: pocos indicios de métricas más allá de memorization")
            else:
                warnings.append("downstream_metrics: ampliar menciones (reasoning, arithmetic, etc.)")

    gates.append(
        {
            "id": "downstream_metrics_declared",
            "passed": downstream_passed,
            "detail": downstream_detail,
        }
    )

    all_passed = all(g["passed"] for g in gates)
    report: dict[str, Any] = {
        "mission_version": mission.mission_version,
        "all_passed": all_passed,
        "gates": gates,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "publishable": all_passed and not blocking,
    }
    return all_passed, report


def write_quality_validation(output_dir: Path, report: dict[str, Any]) -> Path:
    p = output_dir / "validation"
    p.mkdir(parents=True, exist_ok=True)
    out = p / "quality_validation.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
