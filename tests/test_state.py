"""Tests for RunState persistence."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.state import RunState, state_path_for


def test_run_state_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    p = state_path_for(out)
    s = RunState.load(p)
    s.mark_done("perplexity:gaps")
    s.perplexity_backend_uuid = "abc-uuid"
    s.save(p)

    s2 = RunState.load(p)
    assert "perplexity:gaps" in s2.completed_steps
    assert s2.perplexity_backend_uuid == "abc-uuid"
