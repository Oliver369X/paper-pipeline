"""Pydantic model for versioned agent_eval baseline JSON (peer-reviewable contract)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BaselineScorecardExpectation(BaseModel):
    """Minimum scorecard fields pinned for regression checks."""

    scenario_pass_rate: float
    safety_correct_rate: float | None
    goal_selection_correct_rate: float | None


class BaselineIntegrityExpectation(BaseModel):
    isolation_ok: bool = True
    evaluator_tampering_detected: bool = False


class AgentEvalBaseline(BaseModel):
    """
    Canonical baseline file shape for ``examples/baselines/agent_eval_baseline.json``.

    Any change to bundled scenarios under ``eval_scenarios/`` must update this file
    and be noted in the PR (see ``examples/baselines/README.md``).
    """

    baseline_format_version: int = 1
    generated_from_commit: str | None = None
    paper_pipeline_version: str | None = None
    expected_scenario_count: int
    expected_scenario_ids: list[str] = Field(
        ...,
        description="Sorted list of scenario ``id`` values; must match bundled scenarios.",
    )
    scorecard: BaselineScorecardExpectation
    integrity: BaselineIntegrityExpectation = Field(default_factory=BaselineIntegrityExpectation)
