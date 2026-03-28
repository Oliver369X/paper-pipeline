"""Goal tree (goals.json) seeding and selection override."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.goals import (
    GoalNode,
    GoalsDocument,
    ensure_goals_seed,
    load_goals_document,
    save_goals_document,
    try_goal_override_from_tree,
)


def test_ensure_goals_seed_creates_pending_root(tmp_path: Path) -> None:
    mission = tmp_path / "mission.md"
    mission.write_text(
        "---\ntopic: Quantum widgets\npaper_target: x\nsections_needed: [gaps]\noutput_dir: outputs\n---\n",
        encoding="utf-8",
    )
    out = tmp_path / "outputs"
    out.mkdir()
    p = ensure_goals_seed(out)
    assert p.is_file()
    doc = load_goals_document(out)
    assert doc is not None
    assert len(doc.nodes) == 1
    assert doc.nodes[0].status == "pending"
    assert doc.nodes[0].goal_type == "literature"
    assert "Quantum widgets" in doc.nodes[0].description


def test_try_goal_override_in_progress_experiment(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    doc = GoalsDocument(
        nodes=[
            GoalNode(
                id="g1",
                description="Ablation study",
                goal_type="experiment",
                status="in_progress",
                priority=0.85,
            )
        ]
    )
    save_goals_document(out, doc)
    sel = try_goal_override_from_tree(out)
    assert sel is not None
    assert sel.selected_goal_type == "experiment"
    assert sel.goal_text == "Ablation study"
    assert "goals.json" in sel.source_signals


def test_invalid_goal_type_skips_override(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    raw = {
        "version": 1,
        "nodes": [
            {
                "id": "bad",
                "description": "x",
                "goal_type": "not_a_valid_type",
                "status": "in_progress",
                "priority": 0.5,
            }
        ],
    }
    (out / "goals.json").write_text(json.dumps(raw), encoding="utf-8")
    assert try_goal_override_from_tree(out) is None
