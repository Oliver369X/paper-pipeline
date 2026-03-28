"""Load scenarios and run oracles against a temp output root."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from .eval_integrity import verify_output_under_root
from .eval_metrics import build_report
from .eval_oracles import match_expectations, run_goal_selection_oracle, run_safety_oracle
from .schemas import EvalReport, EvalScenario, ScenarioResult

logger = logging.getLogger(__name__)


def scenarios_dir_default() -> Path:
    return Path(__file__).resolve().parent / "eval_scenarios"


def load_scenario(path: Path) -> EvalScenario:
    data = json.loads(path.read_text(encoding="utf-8"))
    return EvalScenario.model_validate(data)


def iter_scenario_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.json"), key=lambda p: p.name)


def run_single_scenario(scenario: EvalScenario, allowed_root: Path) -> ScenarioResult:
    axes = list(scenario.axis)
    base_detail: dict = {"target": scenario.target, "axes": axes}

    if scenario.target == "safety":
        decision, detail = run_safety_oracle(scenario)
        ok, errors = match_expectations(scenario, safety_decision=decision)
        return ScenarioResult(
            scenario_id=scenario.id,
            target=scenario.target,
            passed=ok,
            detail={**base_detail, **detail, "errors": errors},
            errors=errors,
        )

    if scenario.target == "goal_selection":
        selection, detail = run_goal_selection_oracle(scenario)
        ok, errors = match_expectations(scenario, goal_selection=selection)
        return ScenarioResult(
            scenario_id=scenario.id,
            target=scenario.target,
            passed=ok,
            detail={**base_detail, **detail, "errors": errors},
            errors=errors,
        )

    if scenario.target == "integrity":
        out = allowed_root / "outputs"
        out.mkdir(parents=True, exist_ok=True)
        ok_path = verify_output_under_root(out, allowed_root)
        ok, errors = match_expectations(scenario, integrity_ok=ok_path)
        return ScenarioResult(
            scenario_id=scenario.id,
            target=scenario.target,
            passed=ok,
            detail={
                **base_detail,
                "isolation_ok": ok_path,
                "errors": errors,
            },
            errors=errors,
        )

    raise ValueError(f"Unknown target: {scenario.target}")


def run_all(allowed_root: Path, *, scenarios_directory: Path | None = None) -> EvalReport:
    sdir = scenarios_directory or scenarios_dir_default()
    results: list[ScenarioResult] = []
    for path in iter_scenario_files(sdir):
        try:
            scenario = load_scenario(path)
        except (ValidationError, json.JSONDecodeError, OSError) as exc:
            logger.warning("Skip invalid scenario %s: %s", path, exc)
            continue
        try:
            results.append(run_single_scenario(scenario, allowed_root))
        except Exception as exc:  # noqa: BLE001
            results.append(
                ScenarioResult(
                    scenario_id=path.stem,
                    target="error",
                    passed=False,
                    detail={"target": "error", "error": str(exc)},
                    errors=[str(exc)],
                )
            )
    return build_report(results)


def run_all_from_dir(scenarios_directory: Path, allowed_root: Path) -> EvalReport:
    return run_all(allowed_root, scenarios_directory=scenarios_directory)
