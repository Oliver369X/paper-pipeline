#!/usr/bin/env python3
"""
Regenerate ``examples/baselines/agent_eval_baseline.json`` from the current bundled scenarios.

Run from the paper-pipeline repo root::

    python scripts/write_agent_eval_baseline.py

Requires the package installed (``pip install -e .``).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from paper_pipeline.agent_eval.baseline_spec import (
    AgentEvalBaseline,
    BaselineIntegrityExpectation,
    BaselineScorecardExpectation,
)
from paper_pipeline.agent_eval.eval_runner import iter_scenario_files, load_scenario, run_all, scenarios_dir_default


def _sorted_scenario_ids(scenarios_dir: Path) -> list[str]:
    ids: list[str] = []
    for path in iter_scenario_files(scenarios_dir):
        scenario = load_scenario(path)
        ids.append(scenario.id)
    return sorted(ids)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / "examples" / "baselines" / "agent_eval_baseline.json"
    sdir = scenarios_dir_default()

    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td), scenarios_directory=sdir)

    sc = report.scorecard
    baseline = AgentEvalBaseline(
        baseline_format_version=1,
        generated_from_commit=None,
        paper_pipeline_version=None,
        expected_scenario_count=len(report.results),
        expected_scenario_ids=_sorted_scenario_ids(sdir),
        scorecard=BaselineScorecardExpectation(
            scenario_pass_rate=sc.scenario_pass_rate,
            safety_correct_rate=sc.safety_correct_rate,
            goal_selection_correct_rate=sc.goal_selection_correct_rate,
        ),
        integrity=BaselineIntegrityExpectation(
            isolation_ok=bool(sc.integrity.get("isolation_ok", True)),
            evaluator_tampering_detected=bool(sc.integrity.get("evaluator_tampering_detected", False)),
        ),
    )

    text = json.dumps(
        baseline.model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )
    out_path.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
