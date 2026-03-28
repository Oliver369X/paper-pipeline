"""Pre/post policy checks for autonomy."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.safety_policy import (
    policy_check_post_action,
    policy_check_pre_goal,
)


def test_policy_pre_blocks_on_triage_errors(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    tri = out / "triage"
    tri.mkdir(parents=True)
    (tri / "triage_report.json").write_text(
        json.dumps({"metrics_validation_errors": ["e1"]}),
        encoding="utf-8",
    )
    r = policy_check_pre_goal(out, selected_goal_type="literature")
    assert r.allowed is False
    assert r.rule_id == "invalid_metrics_block_autonomy"
    assert "e1" in r.reasons


def test_policy_pre_ok_without_triage(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    r = policy_check_pre_goal(out, selected_goal_type="literature")
    assert r.allowed is True


def test_policy_post_dry_run_ok(tmp_path: Path) -> None:
    r = policy_check_post_action(tmp_path / "outputs", dry_run=True)
    assert r.allowed is True
