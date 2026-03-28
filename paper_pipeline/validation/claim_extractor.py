"""Heuristic claim extraction from draft markdown."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from paper_pipeline.mission import Mission


_QUANT = re.compile(r"\b\d+(?:\.\d+)?%|\b\d+(?:\.\d+)?\s*(?:x|×|times|fold)\b", re.I)
_STRONG = re.compile(r"\b(state[- ]of[- ]the[- ]art|SOTA|outperforms|beats|best)\b", re.I)


def extract_claims_from_draft(draft_path: Path) -> list[dict[str, Any]]:
    """Return lightweight claim candidates (deterministic, no LLM)."""

    if not draft_path.is_file():
        return []
    text = draft_path.read_text(encoding="utf-8")
    claims: list[dict[str, Any]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if len(stripped) < 12:
            continue
        ctype = "general"
        if _QUANT.search(stripped):
            ctype = "quantitative"
        elif _STRONG.search(stripped):
            ctype = "literature_or_performance"
        else:
            continue
        claims.append(
            {
                "claim_id": f"line_{i}",
                "line": i,
                "text": stripped[:500],
                "type": ctype,
                "evidence_status": "unverified",
                "evidence_source": None,
            }
        )
    return claims


def write_claims_json(output_dir: Path, draft_path: Path) -> Path:
    out = output_dir / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    claims = extract_claims_from_draft(draft_path)
    p = out / "claims.json"
    p.write_text(json.dumps(claims, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def write_claims_evidence_checklist(
    output_dir: Path,
    draft_path: Path,
    *,
    mission: Mission | None = None,
) -> Path:
    """Structured checklist for claims vs evidence (human or external review)."""

    out = output_dir / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    claims = extract_claims_from_draft(draft_path)
    checklist = {
        "schema_version": 1,
        "note": "evidence_status unverified until human or external tool confirms source",
        "paper_target_hint": "cross-check arXiv ID matches the paper you cite (see docs/ARXIV_TARGET_ALIGNMENT.md)",
        "replication_phase": getattr(mission, "replication_phase", "") if mission else "",
        "replication_fidelity": getattr(mission, "replication_fidelity", "") if mission else "",
        "items": claims,
    }
    p = out / "claims_evidence_checklist.json"
    p.write_text(json.dumps(checklist, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def write_claim_provenance(output_dir: Path, draft_path: Path, *, mission: Mission | None = None) -> Path:
    """Sidecar: etiquetas por claim (v1 heurística + vínculo al checklist)."""

    out = output_dir / "evidence"
    out.mkdir(parents=True, exist_ok=True)
    claims = extract_claims_from_draft(draft_path)
    items: list[dict[str, Any]] = []
    for c in claims:
        cid = c.get("claim_id", "")
        items.append(
            {
                "claim_id": cid,
                "provenance_label": "unclassified",
                "phase_hint": (getattr(mission, "replication_phase", "") or "") if mission else "",
                "notes": "Clasificar como paper_supported | system_proposed | hypothesis | measured",
            }
        )
    payload = {
        "schema_version": 1,
        "items": items,
        "checklist_path": "evidence/claims_evidence_checklist.json",
    }
    p = out / "claim_provenance.json"
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
