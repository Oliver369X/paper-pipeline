"""Regression tests for examples/safety_usecase P2 bundle (no network)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from paper_pipeline.validation.claim_extractor import extract_claims_from_draft

def _usecase_root() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "safety_usecase"


def test_fixture_claims_match_committed_json() -> None:
    root = _usecase_root()
    draft = root / "fixture_draft.md"
    committed = root / "outputs" / "evidence" / "claims.json"
    assert draft.is_file(), "missing fixture_draft.md"
    assert committed.is_file(), "run: python scripts/safety_usecase_repro.py"
    got = extract_claims_from_draft(draft)
    expected = json.loads(committed.read_text(encoding="utf-8"))
    assert got == expected
    assert len(got) >= 1


def test_manifest_sha256_matches_fixture() -> None:
    root = _usecase_root()
    draft = root / "fixture_draft.md"
    man_path = root / "outputs" / "manifest.json"
    assert man_path.is_file()
    man = json.loads(man_path.read_text(encoding="utf-8"))
    h = hashlib.sha256(draft.read_bytes()).hexdigest()
    assert man.get("fixture_sha256") == h
    assert man.get("claims_count") == len(json.loads((root / "outputs" / "evidence" / "claims.json").read_text()))


def test_write_claims_matches_committed_bundle(tmp_path: Path) -> None:
    """Same pipeline path as ``safety_usecase_repro.py`` for claims.json."""
    from paper_pipeline.validation.claim_extractor import write_claims_json

    root = _usecase_root()
    draft = root / "fixture_draft.md"
    write_claims_json(tmp_path, draft)
    a = json.loads((tmp_path / "evidence" / "claims.json").read_text(encoding="utf-8"))
    b = json.loads((root / "outputs" / "evidence" / "claims.json").read_text(encoding="utf-8"))
    assert a == b
