"""Ledger merge after triage + publish."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.ledger.writer import LedgerWriter, merge_ledger_after_triage


def test_merge_ledger_after_triage(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    w = LedgerWriter(out)
    w.start(mission_id="m1", mission_version=1, phase_names=["a"])
    w.finalize("completed")

    (out / "triage").mkdir(parents=True)
    (out / "triage" / "triage_report.json").write_text(
        json.dumps({"tier": 2, "label": "sota_match"}),
        encoding="utf-8",
    )
    (out / "publication").mkdir(parents=True)
    (out / "publication" / "publish_decision.json").write_text(
        json.dumps(
            {
                "eligible_for_publication": True,
                "blocking_reasons": [],
            },
        ),
        encoding="utf-8",
    )

    assert merge_ledger_after_triage(out) is True
    data = json.loads((out / "run_ledger.json").read_text(encoding="utf-8"))
    assert data["decision"]["triage_tier"] == 2
    assert data["decision"]["publishable"] is True
    assert data["decision"]["blocking_reasons"] == []
