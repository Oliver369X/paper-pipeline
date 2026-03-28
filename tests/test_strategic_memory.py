"""Working memory + hypotheses registry (V2 thin)."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.agent.goal_selection import GoalSelection
from paper_pipeline.agent.strategic_memory import (
    HYPOTHESES_REGISTRY_NAME,
    WORKING_MEMORY_NAME,
    WorkingMemoryState,
    ensure_hypotheses_registry,
    load_hypotheses_registry,
    load_working_memory,
    save_working_memory,
    update_strategic_memory_artifacts,
)


def test_working_memory_roundtrip(tmp_path: Path) -> None:
    wm = WorkingMemoryState(
        current_goal_type="literature",
        goal_text_snapshot="Explore RW",
        reason_snapshot="default",
    )
    p = save_working_memory(tmp_path, wm)
    assert p.name == WORKING_MEMORY_NAME
    loaded = load_working_memory(p)
    assert loaded is not None
    assert loaded.current_goal_type == "literature"


def test_ensure_hypotheses_registry_creates_empty(tmp_path: Path) -> None:
    p = ensure_hypotheses_registry(tmp_path)
    assert p.name == HYPOTHESES_REGISTRY_NAME
    reg = load_hypotheses_registry(p)
    assert reg is not None
    assert reg.hypotheses == []


def test_update_strategic_memory_from_goal_selection(tmp_path: Path) -> None:
    sel = GoalSelection(
        selected_goal_type="verification",
        goal_text="Check claims",
        priority=0.9,
        reason="blocked",
    )
    wp, hp = update_strategic_memory_artifacts(tmp_path, sel)
    assert wp.is_file()
    assert hp.is_file()
    wm = load_working_memory(tmp_path / WORKING_MEMORY_NAME)
    assert wm is not None
    assert wm.current_goal_type == "verification"
