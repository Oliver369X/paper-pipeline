"""Pydantic models for agent evaluation scenarios and reports."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TargetKind = Literal["safety", "goal_selection", "integrity"]


class EvalExpectations(BaseModel):
    """Oracle expectations per target."""

    decision: str | None = None
    rule_id: str | None = None
    selected_goal_type: str | None = None
    isolation_ok: bool | None = None


class EvalScenario(BaseModel):
    """One JSON scenario file."""

    id: str
    description: str = ""
    target: TargetKind
    axis: list[str] = Field(default_factory=list)
    simulated_cost: float = 0.0
    safety_context: dict[str, Any] = Field(default_factory=dict)
    goal_inputs: dict[str, Any] = Field(default_factory=dict)
    expectations: EvalExpectations = Field(default_factory=EvalExpectations)


class ScenarioResult(BaseModel):
    scenario_id: str
    target: str
    passed: bool
    detail: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class Scorecard(BaseModel):
    scenario_pass_rate: float
    safety_correct_rate: float | None
    goal_selection_correct_rate: float | None
    by_scenario: dict[str, bool]
    axes: dict[str, dict[str, int]]
    integrity: dict[str, Any]


class EvalReport(BaseModel):
    version: int = 1
    scenarios_run: int
    scenarios_passed: int
    results: list[ScenarioResult]
    scorecard: Scorecard
