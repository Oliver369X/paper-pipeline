"""Deterministic oracles for Safety and Goal selection."""

from __future__ import annotations

from typing import Any

from paper_pipeline.agent.goal_selection import GoalSelection, GoalSelectionInputs, GoalSelector
from paper_pipeline.agent.safety import SafetyContext, SafetyController, SafetyDecision

from .schemas import EvalExpectations, EvalScenario


def run_safety_oracle(scenario: EvalScenario) -> tuple[SafetyDecision, dict[str, Any]]:
    ctx = SafetyContext.model_validate(scenario.safety_context)
    decision = SafetyController().evaluate(ctx)
    detail = {
        "decision": decision.decision,
        "rule_id": decision.rule_id,
    }
    return decision, detail


def run_goal_selection_oracle(scenario: EvalScenario) -> tuple[GoalSelection, dict[str, Any]]:
    inputs = GoalSelectionInputs.model_validate(scenario.goal_inputs)
    selection = GoalSelector().select(inputs)
    detail = {
        "selected_goal_type": selection.selected_goal_type,
        "goal_text": selection.goal_text,
    }
    return selection, detail


def match_expectations(
    scenario: EvalScenario,
    *,
    safety_decision: SafetyDecision | None = None,
    goal_selection: GoalSelection | None = None,
    integrity_ok: bool | None = None,
) -> tuple[bool, list[str]]:
    ex: EvalExpectations = scenario.expectations
    errors: list[str] = []

    if scenario.target == "safety":
        assert safety_decision is not None
        if ex.decision is not None and safety_decision.decision != ex.decision:
            errors.append(f"decision: got {safety_decision.decision}, want {ex.decision}")
        if ex.rule_id is not None and safety_decision.rule_id != ex.rule_id:
            errors.append(f"rule_id: got {safety_decision.rule_id}, want {ex.rule_id}")

    elif scenario.target == "goal_selection":
        assert goal_selection is not None
        if ex.selected_goal_type is not None and goal_selection.selected_goal_type != ex.selected_goal_type:
            errors.append(
                f"selected_goal_type: got {goal_selection.selected_goal_type}, want {ex.selected_goal_type}"
            )

    elif scenario.target == "integrity":
        if ex.isolation_ok is not None and integrity_ok is not None and integrity_ok != ex.isolation_ok:
            errors.append(f"isolation_ok: got {integrity_ok}, want {ex.isolation_ok}")

    return (len(errors) == 0, errors)
