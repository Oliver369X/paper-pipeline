"""ObjectiveState V1 contract and persistence tests."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.objective_state import (
    ObjectiveBuilder,
    ObjectiveInputs,
    ObjectiveState,
    load_objective_state,
    save_objective_state,
)
from paper_pipeline.agent.objective_trace import append_objective_trace


def test_objective_state_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    state = ObjectiveState(
        root_objective="Maximizar evidencia reproducible",
        status="healthy",
        utility_total=1.2,
        terms={
            "contribution_estimate": 0.8,
            "quality_score": 1.0,
            "cost_score": 0.1,
            "risk_score": 0.2,
            "coherence_score": 0.9,
        },
        gates={
            "metrics_valid": True,
            "publishable": True,
            "loop_stopped": False,
            "requires_human_approval": False,
        },
        source_artifacts=["run_ledger.json"],
    )

    path = save_objective_state(out, state)
    loaded = load_objective_state(path)

    assert path.is_file()
    assert loaded.root_objective == state.root_objective
    assert loaded.utility_total == state.utility_total
    assert loaded.gates["publishable"] is True


def test_objective_builder_scores_healthy_run() -> None:
    builder = ObjectiveBuilder()
    inputs = ObjectiveInputs(
        root_objective="Maximizar evidencia reproducible",
        quality_validation={"publishable": True, "blocking_reasons": []},
        triage_report={"tier": 2, "label": "sota_match"},
        publish_decision={"eligible_for_publication": True, "blocking_reasons": []},
        run_ledger={"status": "completed", "phases": [{"name": "final_decision", "status": "done"}]},
    )

    state = builder.build(inputs)

    assert state.status == "healthy"
    assert state.gates["publishable"] is True
    assert state.gates["metrics_valid"] is True
    assert state.utility_total > 0


def test_objective_builder_penalizes_blocking_reasons() -> None:
    builder = ObjectiveBuilder()
    inputs = ObjectiveInputs(
        root_objective="Maximizar evidencia reproducible",
        quality_validation={"publishable": False, "blocking_reasons": ["quality gates"]},
        publish_decision={"eligible_for_publication": False, "blocking_reasons": ["quality gates"]},
    )

    state = builder.build(inputs)

    assert state.gates["publishable"] is False
    assert state.terms["risk_score"] > 0
    assert state.utility_total < 0


def test_objective_builder_penalizes_loop_stop() -> None:
    builder = ObjectiveBuilder()
    inputs = ObjectiveInputs(
        root_objective="Maximizar evidencia reproducible",
        loop_stop_decision={"status": "stopped", "reasons": ["draft_stalled_or_minimal_delta"]},
    )

    state = builder.build(inputs)

    assert state.gates["loop_stopped"] is True
    assert state.status == "stalled"
    assert state.utility_total < 0


def test_append_objective_trace_writes_jsonl(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    state = ObjectiveState(
        root_objective="Maximizar evidencia reproducible",
        status="healthy",
        utility_total=0.5,
        terms={
            "contribution_estimate": 0.5,
            "quality_score": 0.5,
            "cost_score": 0.1,
            "risk_score": 0.1,
            "coherence_score": 0.7,
        },
        gates={
            "metrics_valid": True,
            "publishable": True,
            "loop_stopped": False,
            "requires_human_approval": False,
        },
        source_artifacts=["publication/publish_decision.json"],
    )

    trace = append_objective_trace(out, state, candidate_action_family="post_pipeline")

    rows = trace.read_text(encoding="utf-8").splitlines()
    payload = json.loads(rows[-1])
    assert payload["candidate_action_family"] == "post_pipeline"
    assert payload["utility_total"] == 0.5
    assert payload["gates"]["publishable"] is True
