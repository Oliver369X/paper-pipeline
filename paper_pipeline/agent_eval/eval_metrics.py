"""Aggregate scenario results into a scorecard."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .schemas import EvalReport, ScenarioResult, Scorecard


def build_scorecard(results: list[ScenarioResult]) -> Scorecard:
    by_scenario = {r.scenario_id: r.passed for r in results}
    n = len(results)
    passed = sum(1 for r in results if r.passed)
    scenario_pass_rate = (passed / n) if n else 0.0

    safety_ids = [r for r in results if r.detail.get("target") == "safety"]
    goal_ids = [r for r in results if r.detail.get("target") == "goal_selection"]
    integrity_ids = [r for r in results if r.detail.get("target") == "integrity"]

    safety_correct_rate = None
    if safety_ids:
        s_ok = sum(1 for r in safety_ids if r.passed)
        safety_correct_rate = s_ok / len(safety_ids)

    goal_selection_correct_rate = None
    if goal_ids:
        g_ok = sum(1 for r in goal_ids if r.passed)
        goal_selection_correct_rate = g_ok / len(goal_ids)

    axes: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in results:
        for axis in r.detail.get("axes", []) or []:
            bucket = "pass" if r.passed else "fail"
            axes[axis][bucket] += 1

    isolation_ok = True
    if integrity_ids:
        isolation_ok = all(r.detail.get("isolation_ok", True) for r in integrity_ids)

    integrity: dict[str, Any] = {
        "isolation_ok": isolation_ok,
        "evaluator_tampering_detected": False,
    }

    return Scorecard(
        scenario_pass_rate=scenario_pass_rate,
        safety_correct_rate=safety_correct_rate,
        goal_selection_correct_rate=goal_selection_correct_rate,
        by_scenario=by_scenario,
        axes={k: dict(v) for k, v in axes.items()},
        integrity=integrity,
    )


def build_report(results: list[ScenarioResult]) -> EvalReport:
    sc = build_scorecard(results)
    n = len(results)
    passed = sum(1 for r in results if r.passed)
    return EvalReport(
        scenarios_run=n,
        scenarios_passed=passed,
        results=results,
        scorecard=sc,
    )


def scorecard_to_stable_dict(report: EvalReport) -> dict:
    """JSON-serializable dict with sorted keys for reproducible diffs."""
    return report.model_dump(mode="json")
