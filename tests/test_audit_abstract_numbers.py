"""Tests for scripts/audit_abstract_numbers.py (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.reporting.abstract_audit import run_audit


def test_run_audit_emits_wall_clock_and_claims(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    (out / "evidence").mkdir(parents=True)
    (out / "triage").mkdir(parents=True)
    (out / "evidence" / "claims.json").write_text(json.dumps([{"x": 1}, {"x": 2}]), encoding="utf-8")
    (out / "triage" / "triage_report.json").write_text(
        json.dumps({"tier": 2, "label": "insufficient_metrics"}),
        encoding="utf-8",
    )
    (out / "metrics.json").write_text(
        json.dumps({"replication_tier": "planning_only"}),
        encoding="utf-8",
    )
    (out / "run_ledger.json").write_text(
        json.dumps(
            {
                "started_at": "2026-01-01T00:00:00+00:00",
                "ended_at": "2026-01-01T00:01:40+00:00",
                "run_id": "test_run",
                "phases": [{"name": "a"}, {"name": "b"}],
            },
        ),
        encoding="utf-8",
    )
    text = run_audit(repo_root=tmp_path, mission_outputs=out)
    assert "100.000 s" in text or "100." in text
    assert "2" in text
    assert "insufficient_metrics" in text
    assert "planning_only" in text
