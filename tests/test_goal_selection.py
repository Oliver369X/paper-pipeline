"""GoalSelection V1 contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.goal_selection import (
    GoalSelection,
    GoalSelectionInputs,
    GoalSelector,
    build_goal_selection_from_output_dir,
    load_goal_selection,
    resolve_goal_text,
    save_goal_selection,
)


def test_build_goal_selection_prefers_in_progress_goal_tree(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    goals = {
        "version": 1,
        "nodes": [
            {
                "id": "n1",
                "parent_id": None,
                "description": "Correr experimento X",
                "goal_type": "experiment",
                "status": "in_progress",
                "priority": 0.88,
            }
        ],
        "mission_topic_hint": "t",
    }
    (out / "goals.json").write_text(json.dumps(goals), encoding="utf-8")
    selection = build_goal_selection_from_output_dir(out)
    assert selection.selected_goal_type == "experiment"
    assert "goals.json" in selection.source_signals


def test_goal_selector_wait_human_on_loop_stop() -> None:
    selector = GoalSelector()
    inputs = GoalSelectionInputs(
        objective_state={
            "status": "stalled",
            "terms": {"contribution_estimate": 0.0},
            "gates": {
                "metrics_valid": True,
                "publishable": False,
                "loop_stopped": True,
                "requires_human_approval": False,
            },
        },
    )

    selection = selector.select(inputs)

    assert selection.selected_goal_type == "wait_human"


def test_goal_selector_wait_human_when_requires_approval() -> None:
    selector = GoalSelector()
    inputs = GoalSelectionInputs(
        objective_state={
            "status": "needs_review",
            "terms": {"contribution_estimate": 1.0},
            "gates": {
                "metrics_valid": True,
                "publishable": True,
                "loop_stopped": False,
                "requires_human_approval": True,
            },
        },
    )

    selection = selector.select(inputs)

    assert selection.selected_goal_type == "wait_human"


def test_goal_selector_prefers_writing_for_publishable_high_contribution() -> None:
    selector = GoalSelector()
    inputs = GoalSelectionInputs(
        objective_state={
            "status": "healthy",
            "terms": {"contribution_estimate": 0.8},
            "gates": {
                "metrics_valid": True,
                "publishable": True,
                "loop_stopped": False,
                "requires_human_approval": False,
            },
        },
    )

    selection = selector.select(inputs)

    assert selection.selected_goal_type == "writing"


def test_goal_selector_prefers_verification_for_blocked_publish() -> None:
    selector = GoalSelector()
    inputs = GoalSelectionInputs(
        objective_state={
            "status": "blocked",
            "terms": {"contribution_estimate": -0.1},
            "gates": {
                "metrics_valid": True,
                "publishable": False,
                "loop_stopped": False,
                "requires_human_approval": False,
            },
        },
        memory_index={
            "latest_by_kind": {
                "publish": {
                    "summary": "Publish bloqueado",
                    "payload": {"eligible_for_publication": False},
                },
            },
        },
    )

    selection = selector.select(inputs)

    assert selection.selected_goal_type == "verification"


def test_goal_selector_recommends_experiment_for_healthy_non_publishable_case() -> None:
    selector = GoalSelector()
    inputs = GoalSelectionInputs(
        objective_state={
            "status": "healthy",
            "terms": {"contribution_estimate": 0.3},
            "gates": {
                "metrics_valid": True,
                "publishable": False,
                "loop_stopped": False,
                "requires_human_approval": False,
            },
        },
    )

    selection = selector.select(inputs)

    assert selection.selected_goal_type == "experiment"


def test_goal_selection_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    selection = GoalSelection(
        selected_goal_type="verification",
        goal_text="Verificar bloqueos de publicación y claims",
        priority=0.8,
        reason="Hay bloqueos activos y conviene revisar evidencia",
        source_signals=["objective_state.json", "memory_index.json"],
        gates={"publishable": False},
    )

    path = save_goal_selection(out, selection)
    loaded = load_goal_selection(path)

    assert path.is_file()
    assert loaded.selected_goal_type == "verification"
    assert loaded.goal_text == selection.goal_text


def test_resolve_goal_text_prefers_explicit_goal(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    save_goal_selection(
        out,
        GoalSelection(
            selected_goal_type="writing",
            goal_text="Consolidar borrador",
            priority=0.8,
            reason="x",
            source_signals=[],
            gates={},
        ),
    )

    resolved = resolve_goal_text(out, explicit_goal="Goal manual", default_goal="Default goal")

    assert resolved == "Goal manual"


def test_resolve_goal_text_uses_saved_selection_when_no_explicit_goal(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    save_goal_selection(
        out,
        GoalSelection(
            selected_goal_type="verification",
            goal_text="Verificar bloqueos activos",
            priority=0.9,
            reason="x",
            source_signals=[],
            gates={},
        ),
    )

    resolved = resolve_goal_text(out, explicit_goal="", default_goal="Default goal")

    assert resolved == "Verificar bloqueos activos"
