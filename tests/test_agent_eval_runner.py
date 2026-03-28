"""Agent eval harness: bundled scenarios and reproducible scorecard."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
from paper_pipeline.agent_eval.eval_runner import run_all, scenarios_dir_default


def test_agent_eval_all_scenarios_pass(tmp_path: Path) -> None:
    report = run_all(tmp_path)
    assert report.scenarios_run >= 12
    assert report.scenarios_passed == report.scenarios_run
    assert report.scorecard.scenario_pass_rate == 1.0
    assert report.scorecard.safety_correct_rate == 1.0
    assert report.scorecard.goal_selection_correct_rate == 1.0
    assert report.scorecard.integrity["isolation_ok"] is True


def test_scorecard_json_stable(tmp_path: Path) -> None:
    r1 = run_all(tmp_path)
    r2 = run_all(tmp_path)
    j1 = json.dumps(scorecard_to_stable_dict(r1), sort_keys=True)
    j2 = json.dumps(scorecard_to_stable_dict(r2), sort_keys=True)
    assert j1 == j2


def test_at_least_two_scenario_kinds_exercised(tmp_path: Path) -> None:
    report = run_all(tmp_path)
    targets = {r.detail.get("target") for r in report.results}
    assert "safety" in targets
    assert "goal_selection" in targets
    assert "integrity" in targets


def test_bundled_scenarios_dir_exists() -> None:
    d = scenarios_dir_default()
    assert d.is_dir()
    assert len(list(d.glob("*.json"))) >= 12


def test_safety_metrics_invalid_direct(tmp_path: Path) -> None:
    """Explicit regression for invalid-metrics BLOCK oracle."""
    from paper_pipeline.agent_eval.eval_runner import load_scenario, run_single_scenario

    path = scenarios_dir_default() / "safety_metrics_invalid.json"
    scenario = load_scenario(path)
    res = run_single_scenario(scenario, tmp_path)
    assert res.passed
    assert res.detail.get("decision") == "BLOCK"


def test_goal_verification_direct(tmp_path: Path) -> None:
    from paper_pipeline.agent_eval.eval_runner import load_scenario, run_single_scenario

    path = scenarios_dir_default() / "goal_verification_blocked.json"
    scenario = load_scenario(path)
    res = run_single_scenario(scenario, tmp_path)
    assert res.passed
    assert res.detail.get("selected_goal_type") == "verification"
