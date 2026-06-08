"""Compare ``EvalReport`` to a pinned ``AgentEvalBaseline`` (deterministic messages)."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .baseline_spec import AgentEvalBaseline
from .schemas import EvalReport


def load_baseline(path: Path) -> AgentEvalBaseline:
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentEvalBaseline.model_validate(data)


def _sorted_ids_from_report(report: EvalReport) -> list[str]:
    return sorted({r.scenario_id for r in report.results})


def compare_report_to_baseline(report: EvalReport, baseline: AgentEvalBaseline) -> list[str]:
    """
    Return a sorted list of human-readable mismatch messages.
    Empty list means the report satisfies the baseline.
    """
    errors: list[str] = []

    if report.scenarios_run != baseline.expected_scenario_count:
        errors.append(
            f"scenarios_run={report.scenarios_run} != baseline.expected_scenario_count="
            f"{baseline.expected_scenario_count}"
        )

    got_ids = _sorted_ids_from_report(report)
    if got_ids != sorted(baseline.expected_scenario_ids):
        errors.append(
            "scenario_ids_mismatch: "
            f"got={got_ids!r} expected={sorted(baseline.expected_scenario_ids)!r}"
        )

    sc = report.scorecard
    bsc = baseline.scorecard
    if sc.scenario_pass_rate != bsc.scenario_pass_rate:
        errors.append(
            f"scenario_pass_rate={sc.scenario_pass_rate} != baseline {bsc.scenario_pass_rate}"
        )
    if sc.safety_correct_rate != bsc.safety_correct_rate:
        errors.append(
            f"safety_correct_rate={sc.safety_correct_rate} != baseline {bsc.safety_correct_rate}"
        )
    if sc.goal_selection_correct_rate != bsc.goal_selection_correct_rate:
        errors.append(
            "goal_selection_correct_rate="
            f"{sc.goal_selection_correct_rate} != baseline {bsc.goal_selection_correct_rate}"
        )

    iso = sc.integrity.get("isolation_ok")
    if iso is not baseline.integrity.isolation_ok:
        errors.append(
            f"integrity.isolation_ok={iso} != baseline {baseline.integrity.isolation_ok}"
        )
    tamper = sc.integrity.get("evaluator_tampering_detected")
    if tamper is not baseline.integrity.evaluator_tampering_detected:
        errors.append(
            "integrity.evaluator_tampering_detected="
            f"{tamper} != baseline {baseline.integrity.evaluator_tampering_detected}"
        )

    return sorted(errors)


def validate_baseline_file(path: Path) -> list[str]:
    """Return parse/validation errors for a baseline JSON file (for tests)."""
    try:
        load_baseline(path)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        return [str(exc)]
    return []
