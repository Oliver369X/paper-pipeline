"""Tests for benchmark_bundle JSON (no matplotlib)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
from paper_pipeline.agent_eval.eval_runner import run_all
from paper_pipeline.reporting.benchmark_bundle import (
    benchmark_bundle_to_markdown_table,
    build_benchmark_bundle,
    ledger_phase_durations_seconds,
)


def test_ledger_phase_durations_seconds_sample() -> None:
    ledger = {
        "started_at": "2026-03-29T06:12:37.821631+00:00",
        "phases": [
            {
                "name": "a",
                "started_at": None,
                "ended_at": "2026-03-29T06:12:38.821631+00:00",
                "status": "done",
            },
            {
                "name": "b",
                "started_at": "2026-03-29T06:12:38.821631+00:00",
                "ended_at": "2026-03-29T06:12:40.821631+00:00",
                "status": "done",
            },
        ],
    }
    rows = ledger_phase_durations_seconds(ledger)
    assert len(rows) == 2
    assert rows[0]["phase"] == "a"
    assert rows[0]["seconds"] >= 0.9
    assert rows[1]["phase"] == "b"
    assert rows[1]["seconds"] >= 1.9


def test_build_benchmark_bundle_has_agent_eval(tmp_path: Path) -> None:
    # repo_root must be real package root for run_all scenarios
    repo_root = Path(__file__).resolve().parents[1]
    b = build_benchmark_bundle(repo_root=repo_root, case_study_outputs=None)
    assert b.get("kind") == "benchmark_bundle"
    assert "agent_eval" in b
    assert b["agent_eval"].get("scenarios_run", 0) >= 1
    assert isinstance(b["agent_eval"].get("per_scenario"), list)


def test_build_benchmark_bundle_with_injected_payload_matches() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td))
    payload = scorecard_to_stable_dict(report)
    a = build_benchmark_bundle(repo_root=repo_root, case_study_outputs=None)
    b = build_benchmark_bundle(
        repo_root=repo_root,
        case_study_outputs=None,
        agent_eval_report_payload=payload,
    )
    assert a["agent_eval"]["scenarios_run"] == b["agent_eval"]["scenarios_run"]
    assert len(a["agent_eval"]["per_scenario"]) == len(b["agent_eval"]["per_scenario"])


def test_benchmark_bundle_to_markdown_table_contains_headers() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    b = build_benchmark_bundle(repo_root=repo_root, case_study_outputs=None)
    md = benchmark_bundle_to_markdown_table(b)
    assert "Agent eval" in md
    assert "scenario_id" in md
