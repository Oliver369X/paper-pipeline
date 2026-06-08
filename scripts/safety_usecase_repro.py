#!/usr/bin/env python3
"""
Regenerate deterministic evidence artifacts for ``examples/safety_usecase/``.

Uses the same claim extraction path as ``run_pipeline`` (no LLM, no network).

Run from repo root::

    python scripts/safety_usecase_repro.py

Writes:

- ``examples/safety_usecase/outputs/evidence/claims.json``
- ``examples/safety_usecase/outputs/evidence/claims_evidence_checklist.json``
- ``examples/safety_usecase/outputs/manifest.json``
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from paper_pipeline.validation.claim_extractor import (
    write_claims_evidence_checklist,
    write_claims_json,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    usecase = repo_root / "examples" / "safety_usecase"
    draft = usecase / "fixture_draft.md"
    out_dir = usecase / "outputs"

    if not draft.is_file():
        raise SystemExit(f"Missing fixture: {draft}")

    write_claims_json(out_dir, draft)
    write_claims_evidence_checklist(out_dir, draft, mission=None)

    claims_path = out_dir / "evidence" / "claims.json"
    payload = json.loads(claims_path.read_text(encoding="utf-8"))
    manifest = {
        "schema_version": 1,
        "kind": "safety_usecase_p2",
        "fixture_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
        "claims_count": len(payload),
        "note": "Regenerate with scripts/safety_usecase_repro.py after editing fixture_draft.md",
    }
    man_path = out_dir / "manifest.json"
    man_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote evidence under {out_dir}")


if __name__ == "__main__":
    main()
