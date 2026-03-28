"""Golden outputs fixture: scheduler sin red (sin Perplexity)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from paper_pipeline.agent.scheduler import AGENT_DECISIONS_NAME, run_agent_step
from paper_pipeline.mission import Mission

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "autonomy_golden" / "outputs"


def test_run_agent_step_golden_fixture_allows_policy(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    shutil.copytree(FIXTURE_ROOT, out)
    mission = Mission(
        topic="Golden",
        paper_target="venue",
        sections_needed=["gaps"],
        mode="autonomy",
    )
    res = run_agent_step(out, mission, dry_run=True)
    assert res["ok"] is True
    rec = res["record"]
    assert rec["dry_run"] is True
    assert rec["policy_pre"]["allowed"] is True
    assert rec["policy_pre"]["rule_id"] == "policy_pre_allow"
    assert rec["safety"]["decision"] == "ALLOW"
    p = out / AGENT_DECISIONS_NAME
    assert p.is_file()


def test_run_agent_step_golden_with_metrics_errors_blocks_policy(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    shutil.copytree(FIXTURE_ROOT, out)
    tri = out / "triage" / "triage_report.json"
    data = json.loads(tri.read_text(encoding="utf-8"))
    data["metrics_validation_errors"] = ["golden_force_error"]
    tri.write_text(json.dumps(data), encoding="utf-8")
    mission = Mission(topic="T", paper_target="p", sections_needed=["gaps"], mode="autonomy")
    res = run_agent_step(out, mission, dry_run=True)
    assert res["record"]["policy_pre"]["allowed"] is False
    assert res["record"]["policy_pre"]["rule_id"] == "invalid_metrics_block_autonomy"
