"""Autonomous scheduler step (dry-run, no Perplexity)."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.scheduler import AGENT_DECISIONS_NAME, run_agent_step
from paper_pipeline.mission import Mission


def test_run_agent_step_writes_decision_jsonl(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (tmp_path / "mission.md").write_text(
        "---\ntopic: T\npaper_target: p\nsections_needed: [gaps]\nmode: autonomy\n---\n",
        encoding="utf-8",
    )
    mission = Mission(
        topic="T",
        paper_target="p",
        sections_needed=["gaps"],
        mode="autonomy",
    )
    res = run_agent_step(out, mission, dry_run=True)
    assert res["ok"] is True
    p = out / AGENT_DECISIONS_NAME
    assert p.is_file()
    line = p.read_text(encoding="utf-8").strip()
    row = json.loads(line)
    assert row["dry_run"] is True
    assert "selected_goal_type" in row
    assert row["safety"]["decision"] in ("ALLOW", "BLOCK", "REQUIRE_HUMAN_APPROVAL", "ALLOW_WITH_RESTRICTIONS")


def test_run_agent_step_respects_loop_stop(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "objective_state.json").write_text(
        json.dumps({"gates": {"loop_stopped": True}, "terms": {}, "status": "blocked"}),
        encoding="utf-8",
    )
    res = run_agent_step(out, None, dry_run=True)
    row = res["record"]
    assert row["safety"]["decision"] == "BLOCK"
    assert row["safety"]["rule_id"] == "loop_stop_blocks_agent_step"
