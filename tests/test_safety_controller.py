"""SafetyController V1 contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.safety import SafetyContext, SafetyController
from paper_pipeline.agent.safety_trace import append_safety_trace


def test_block_publish_when_metrics_invalid() -> None:
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="publish_consolidation",
        metrics_validation_errors=["coverage > 1"],
    )

    decision = controller.evaluate(ctx)

    assert decision.decision == "BLOCK"
    assert decision.rule_id == "invalid_metrics_block_publish"
    assert "metrics validation failed" in " ".join(decision.reasons).lower()


def test_require_human_for_breakthrough_publication() -> None:
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="publish_consolidation",
        triage_tier=3,
        eligible_for_publication=True,
    )

    decision = controller.evaluate(ctx)

    assert decision.decision == "REQUIRE_HUMAN_APPROVAL"
    assert decision.rule_id == "breakthrough_requires_human_approval"


def test_block_publish_when_blocking_reasons_exist() -> None:
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="publish_consolidation",
        publish_blocking_reasons=["quality gates"],
    )

    decision = controller.evaluate(ctx)

    assert decision.decision == "BLOCK"
    assert decision.rule_id == "publish_blocking_reasons"


def test_block_agent_step_when_loop_stopped() -> None:
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="agent_step",
        loop_stop_reasons=["stall"],
    )
    decision = controller.evaluate(ctx)
    assert decision.decision == "BLOCK"
    assert decision.rule_id == "loop_stop_blocks_agent_step"


def test_block_agent_step_when_metrics_invalid() -> None:
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="agent_step",
        metrics_validation_errors=["bad"],
    )
    decision = controller.evaluate(ctx)
    assert decision.decision == "BLOCK"
    assert decision.rule_id == "invalid_metrics_block_agent_step"


def test_allow_when_no_red_flags() -> None:
    controller = SafetyController()
    ctx = SafetyContext(candidate_action="publish_consolidation", eligible_for_publication=True)

    decision = controller.evaluate(ctx)

    assert decision.decision == "ALLOW"
    assert decision.rule_id == "allow_default"


def test_append_safety_trace_writes_jsonl(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    controller = SafetyController()
    ctx = SafetyContext(
        candidate_action="publish_consolidation",
        triage_tier=3,
        eligible_for_publication=True,
        mission_id="m1",
        run_id="r1",
        source_artifacts=["triage/triage_report.json", "publication/publish_decision.json"],
    )
    decision = controller.evaluate(ctx)

    trace_path = append_safety_trace(out, ctx, decision)

    assert trace_path.is_file()
    rows = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    payload = json.loads(rows[0])
    assert payload["decision"] == "REQUIRE_HUMAN_APPROVAL"
    assert payload["rule_id"] == "breakthrough_requires_human_approval"
    assert payload["candidate_action"] == "publish_consolidation"
    assert payload["mission_id"] == "m1"
    assert payload["run_id"] == "r1"
