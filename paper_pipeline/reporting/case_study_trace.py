"""Build a redacted ``case_study_trace.json`` from a mission ``outputs/`` tree (no secrets)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def build_case_study_trace(outputs_dir: Path) -> dict[str, Any]:
    """
    Aggregate audit-friendly fields for supplementary material.

    ``outputs_dir`` is the mission ``outputs/`` folder (containing run_ledger.json, etc.).
    Paths inside JSON are relative names only; no environment or tokens.
    """
    out: dict[str, Any] = {
        "schema_version": 1,
        "kind": "case_study_trace",
        "outputs_dir_hint": "mission outputs/ root (relative names below)",
        "artifacts_present": [],
    }
    ledger = _read_json(outputs_dir / "run_ledger.json")
    if isinstance(ledger, dict):
        out["mission_id"] = ledger.get("mission_id")
        out["run_id"] = ledger.get("run_id")
        out["ledger_status"] = ledger.get("status")
        out["started_at"] = ledger.get("started_at")
        out["ended_at"] = ledger.get("ended_at")
        phases = ledger.get("phases")
        if isinstance(phases, list):
            out["phases"] = [
                {
                    "name": p.get("name"),
                    "status": p.get("status"),
                    "ended_at": p.get("ended_at"),
                    "error": p.get("error"),
                }
                for p in phases
                if isinstance(p, dict)
            ]

    man = _read_json(outputs_dir / "manifest.json")
    if isinstance(man, dict):
        out["manifest_summary"] = {k: man.get(k) for k in ("schema_version", "mission_id") if k in man}

    pub = _read_json(outputs_dir / "publication" / "publish_decision.json")
    if isinstance(pub, dict):
        out["publish_decision"] = {
            "eligible_for_publication": pub.get("eligible_for_publication"),
            "triage_tier": pub.get("triage_tier"),
            "triage_label": pub.get("triage_label"),
            "blocking_reasons": pub.get("blocking_reasons"),
        }

    tri = _read_json(outputs_dir / "triage" / "triage_report.json")
    if isinstance(tri, dict):
        out["triage"] = {
            "tier": tri.get("tier"),
            "label": tri.get("label"),
            "reason": tri.get("reason"),
        }

    met = _read_json(outputs_dir / "metrics.json")
    if isinstance(met, dict):
        out["metrics_summary"] = {
            "schema_version": met.get("schema_version"),
            "exit_code": met.get("exit_code"),
            "replication_tier": met.get("replication_tier"),
            "experiment_runner": met.get("experiment_runner"),
        }

    claims_path = outputs_dir / "evidence" / "claims.json"
    claims = _read_json(claims_path)
    if isinstance(claims, list):
        out["claims_extracted_count"] = len(claims)
        out["claims_types"] = _count_claim_types(claims)

    for rel in (
        "run_ledger.json",
        "manifest.json",
        "metrics.json",
        "draft_paper.md",
        "evidence/claims.json",
        "publication/publish_decision.json",
        "triage/triage_report.json",
        "replication_status.md",
    ):
        if (outputs_dir / rel).is_file():
            out["artifacts_present"].append(rel)

    out["note"] = (
        "Redacted summary for reproducibility reporting; does not include API payloads, "
        "tokens, or full draft text."
    )
    return out


def _count_claim_types(claims: list[Any]) -> dict[str, int]:
    from collections import Counter

    c: Counter[str] = Counter()
    for item in claims:
        if isinstance(item, dict):
            c[str(item.get("type", "unknown"))] += 1
    return dict(c)


def build_minimal_safety_usecase_trace(repo_root: Path) -> dict[str, Any]:
    """Fallback when no full mission outputs exist: P2 fixture only."""
    usecase = repo_root / "examples" / "safety_usecase"
    manifest = _read_json(usecase / "outputs" / "manifest.json")
    claims = _read_json(usecase / "outputs" / "evidence" / "claims.json")
    n = len(claims) if isinstance(claims, list) else 0
    return {
        "schema_version": 1,
        "kind": "case_study_trace",
        "variant": "safety_usecase_p2_fixture",
        "paper_anchor_arxiv": "2510.24256",
        "manifest": manifest if isinstance(manifest, dict) else {},
        "claims_extracted_count": n,
        "note": "Deterministic CI bundle from examples/safety_usecase; not a full mission ledger.",
    }
