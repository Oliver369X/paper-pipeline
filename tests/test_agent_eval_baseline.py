"""Regression tests for pinned agent_eval baseline JSON.

Maps to preprint §4 (Evaluation / agent_eval harness): baseline regression protects
the claim that bundled governance scenarios remain deterministic at pass rate 1.0.
"""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.agent_eval.baseline_compare import (
    compare_report_to_baseline,
    load_baseline,
    validate_baseline_file,
)
from paper_pipeline.agent_eval.eval_runner import run_all


def _baseline_path() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "baselines" / "agent_eval_baseline.json"


def test_repo_baseline_file_validates() -> None:
    err = validate_baseline_file(_baseline_path())
    assert err == []


def test_run_all_matches_repo_baseline(tmp_path: Path) -> None:
    # §4 — primary regression: full harness matches pinned baseline JSON.
    baseline = load_baseline(_baseline_path())
    report = run_all(tmp_path)
    errors = compare_report_to_baseline(report, baseline)
    assert errors == []


def test_compare_fails_on_wrong_scenario_count(tmp_path: Path) -> None:
    baseline = load_baseline(_baseline_path())
    baseline = baseline.model_copy(update={"expected_scenario_count": 1})
    report = run_all(tmp_path)
    errors = compare_report_to_baseline(report, baseline)
    assert any("scenarios_run=" in e for e in errors)


def test_compare_fails_on_wrong_pass_rate(tmp_path: Path) -> None:
    baseline = load_baseline(_baseline_path())
    sc = baseline.scorecard.model_copy(update={"scenario_pass_rate": 0.0})
    baseline = baseline.model_copy(update={"scorecard": sc})
    report = run_all(tmp_path)
    errors = compare_report_to_baseline(report, baseline)
    assert any("scenario_pass_rate=" in e for e in errors)


def test_compare_fails_on_scenario_ids_mismatch(tmp_path: Path) -> None:
    baseline = load_baseline(_baseline_path())
    ids = list(baseline.expected_scenario_ids)
    ids[0] = "nonexistent_scenario_id"
    baseline = baseline.model_copy(update={"expected_scenario_ids": sorted(ids)})
    report = run_all(tmp_path)
    errors = compare_report_to_baseline(report, baseline)
    assert any("scenario_ids_mismatch" in e for e in errors)


def test_invalid_json_baseline_errors(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{", encoding="utf-8")
    err = validate_baseline_file(p)
    assert len(err) >= 1
