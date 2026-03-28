"""SafetyController V1: explicit governance decisions from existing artifacts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SafetyOutcome = Literal["ALLOW", "ALLOW_WITH_RESTRICTIONS", "REQUIRE_HUMAN_APPROVAL", "BLOCK"]


class SafetyContext(BaseModel):
    candidate_action: str
    mission_id: str | None = None
    run_id: str | None = None
    triage_tier: int | None = None
    eligible_for_publication: bool = False
    loop_stop_reasons: list[str] = Field(default_factory=list)
    metrics_validation_errors: list[str] = Field(default_factory=list)
    publish_blocking_reasons: list[str] = Field(default_factory=list)
    source_artifacts: list[str] = Field(default_factory=list)


class SafetyDecision(BaseModel):
    decision: SafetyOutcome
    rule_id: str
    reasons: list[str] = Field(default_factory=list)
    source_artifacts: list[str] = Field(default_factory=list)


class SafetyController:
    """Pure policy layer over existing repo signals."""

    def evaluate(self, context: SafetyContext) -> SafetyDecision:
        if context.candidate_action == "loop_iteration" and context.loop_stop_reasons:
            return SafetyDecision(
                decision="BLOCK",
                rule_id="loop_stop_decision",
                reasons=["Loop stop policy triggered."] + list(context.loop_stop_reasons),
                source_artifacts=context.source_artifacts,
            )

        if context.candidate_action == "publish_consolidation" and context.metrics_validation_errors:
            return SafetyDecision(
                decision="BLOCK",
                rule_id="invalid_metrics_block_publish",
                reasons=["Metrics validation failed; publication cannot be promoted."],
                source_artifacts=context.source_artifacts,
            )

        if context.candidate_action == "publish_consolidation" and context.publish_blocking_reasons:
            return SafetyDecision(
                decision="BLOCK",
                rule_id="publish_blocking_reasons",
                reasons=[
                    "Publish decision contains blocking reasons."
                ]
                + list(context.publish_blocking_reasons),
                source_artifacts=context.source_artifacts,
            )

        if (
            context.candidate_action == "publish_consolidation"
            and context.triage_tier == 3
            and context.eligible_for_publication
        ):
            return SafetyDecision(
                decision="REQUIRE_HUMAN_APPROVAL",
                rule_id="breakthrough_requires_human_approval",
                reasons=["Breakthrough-tier publication requires explicit human approval."],
                source_artifacts=context.source_artifacts,
            )

        if context.candidate_action == "agent_step" and context.loop_stop_reasons:
            return SafetyDecision(
                decision="BLOCK",
                rule_id="loop_stop_blocks_agent_step",
                reasons=["Loop stopped; autonomous step blocked until human review."]
                + list(context.loop_stop_reasons),
                source_artifacts=context.source_artifacts,
            )

        if context.candidate_action == "agent_step" and context.metrics_validation_errors:
            return SafetyDecision(
                decision="BLOCK",
                rule_id="invalid_metrics_block_agent_step",
                reasons=["Metrics validation failed; autonomous step blocked."]
                + list(context.metrics_validation_errors),
                source_artifacts=context.source_artifacts,
            )

        return SafetyDecision(
            decision="ALLOW",
            rule_id="allow_default",
            reasons=["No hard safety constraints triggered."],
            source_artifacts=context.source_artifacts,
        )

