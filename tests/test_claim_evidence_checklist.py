"""Claims evidence checklist (deterministic)."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.validation.claim_extractor import (
    extract_claims_from_draft,
    write_claims_evidence_checklist,
)


def test_extract_claims_include_evidence_fields(tmp_path: Path) -> None:
    d = tmp_path / "draft.md"
    d.write_text("We achieve 95% accuracy on the test set.\n", encoding="utf-8")
    claims = extract_claims_from_draft(d)
    assert claims
    assert claims[0].get("evidence_status") == "unverified"


def test_write_claims_evidence_checklist_schema(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    d = tmp_path / "draft.md"
    d.write_text("Model outperforms SOTA by 2%.\n", encoding="utf-8")
    p = write_claims_evidence_checklist(out, d)
    assert p.name == "claims_evidence_checklist.json"
    text = p.read_text(encoding="utf-8")
    assert "schema_version" in text
    assert "paper_target_hint" in text
