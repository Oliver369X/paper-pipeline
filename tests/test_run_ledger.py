"""Run ledger writer."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.ledger.writer import LedgerWriter


def test_ledger_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    w = LedgerWriter(out)
    w.start(mission_id="abc", mission_version=1, phase_names=["a", "b"])
    w.upsert_phase("a", "done")
    w.upsert_phase("b", "running")
    w.upsert_phase("b", "done")
    w.finalize("completed")
    data = json.loads((out / "run_ledger.json").read_text(encoding="utf-8"))
    assert data["status"] == "completed"
    assert len(data["phases"]) == 2
