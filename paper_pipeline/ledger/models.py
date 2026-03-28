"""Pydantic models for the canonical run ledger."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

LedgerStatus = Literal["pending", "running", "completed", "failed", "cancelled"]
PhaseName = str


class LedgerPhase(BaseModel):
    """One pipeline phase entry."""

    name: PhaseName
    status: Literal["pending", "running", "done", "failed", "skipped"] = "pending"
    started_at: str | None = None
    ended_at: str | None = None
    artifacts: list[str] = Field(default_factory=list)
    error: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class LedgerIntegrations(BaseModel):
    perplexity: dict[str, Any] = Field(default_factory=dict)
    notion: dict[str, Any] = Field(default_factory=dict)
    cursor_cli: dict[str, Any] = Field(default_factory=dict)


class LedgerDecision(BaseModel):
    triage_tier: int | None = None
    publishable: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)


class RunLedger(BaseModel):
    """Single source of truth for a pipeline run (canonical).

    ``manifest.json`` may be derived from this for backward compatibility.
    """

    schema_version: int = 1
    run_id: str = ""
    mission_id: str = ""
    mission_version: int = 1
    status: LedgerStatus = "pending"
    current_phase: str | None = None
    started_at: str = ""
    ended_at: str | None = None
    phases: list[LedgerPhase] = Field(default_factory=list)
    integrations: LedgerIntegrations = Field(default_factory=LedgerIntegrations)
    decision: LedgerDecision = Field(default_factory=LedgerDecision)
    artifacts_index: dict[str, list[str]] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)

    def model_dump_json_line(self) -> str:
        import json

        return json.dumps(self.model_dump(mode="python"), ensure_ascii=False)

    @classmethod
    def new_run(
        cls,
        *,
        run_id: str,
        mission_id: str,
        mission_version: int,
        phase_names: list[str],
    ) -> RunLedger:
        now = datetime.now(UTC).isoformat()
        return cls(
            run_id=run_id,
            mission_id=mission_id,
            mission_version=mission_version,
            status="running",
            started_at=now,
            current_phase=phase_names[0] if phase_names else None,
            phases=[
                LedgerPhase(name=n, status="pending") for n in phase_names
            ],
        )


def run_ledger_json_schema() -> dict[str, Any]:
    return RunLedger.model_json_schema()
