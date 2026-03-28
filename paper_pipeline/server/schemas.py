"""Pydantic models for REST API (distinct from Mission)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from paper_pipeline.mission import ExperimentRunnerPatch, Hypothesis


class MissionMeta(BaseModel):
    """UI metadata stored in meta.json."""

    title: str = "Untitled paper"
    description: str = ""


class QualityGatesPatch(BaseModel):
    """Partial nested patch for ``Mission.quality_gates`` (merge over existing)."""

    model_config = ConfigDict(extra="forbid")

    target_metric: str | None = None
    higher_is_better: bool | None = None
    sota_baseline_value: float | None = None
    breakthrough_margin: float | None = None
    replication_tolerance: float | None = None
    require_statistical_significance: bool | None = None
    epistemic_alignment_mode: str | None = None
    downstream_metrics_mode: str | None = None


class MissionCreate(BaseModel):
    title: str = "Nuevo paper"
    description: str = ""
    mission_version: int = Field(default=1, ge=1, le=2)
    topic: str = "Research topic"
    paper_target: str = "generic venue"
    sections_needed: list[str] = Field(default_factory=lambda: ["gaps", "methodology", "experiments"])
    max_perplexity_calls: int = Field(default=8, ge=1, le=64)
    code_needed: bool = False
    enable_quality_check: bool = True
    enable_cursor_cli: bool = False
    cursor_cli_optional: bool = True
    enable_notion: bool = False
    notion_page_id: str | None = None
    model: str = "best"
    language: str = "en-US"
    single_thread_perplexity: bool = False
    save_perplexity_to_library: bool = True
    #: Pipeline 2.0 opt-ins (mirrors :class:`~paper_pipeline.mission.Mission`).
    enable_epistemic_injection: bool = False
    enable_degradation_monitor: bool = False
    enable_skill_orchestrator: bool = False
    enable_hypervisor_triage: bool = False
    enable_experiment_runner: bool = False
    parallel_allowed_command_prefixes: list[str] | None = None
    replication_phase: str | None = None
    replication_phase_a_scope: str | None = None
    replication_phase_b_scope: str | None = None
    replication_fidelity: str | None = None
    #: Opcional; si se omite, se usan defaults de :class:`~paper_pipeline.mission.ExperimentRunnerConfig`.
    experiment_runner: ExperimentRunnerPatch | None = None


class MissionPatch(BaseModel):
    """Partial update: only keys present in the JSON body are applied.

    Omitted fields leave existing values in ``mission.md`` / ``meta.json`` unchanged.
    Use explicit ``false`` or ``null`` as needed for booleans and optional strings.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    mission_version: int | None = Field(default=None, ge=1, le=2)
    mode: str | None = None
    topic: str | None = None
    paper_target: str | None = None
    sections_needed: list[str] | None = None
    max_perplexity_calls: int | None = Field(default=None, ge=1, le=64)
    code_needed: bool | None = None
    enable_quality_check: bool | None = None
    enable_cursor_cli: bool | None = None
    cursor_cli_optional: bool | None = None
    enable_notion: bool | None = None
    notion_page_id: str | None = None
    model: str | None = None
    language: str | None = None
    single_thread_perplexity: bool | None = None
    save_perplexity_to_library: bool | None = None
    enable_epistemic_injection: bool | None = None
    enable_degradation_monitor: bool | None = None
    enable_skill_orchestrator: bool | None = None
    enable_hypervisor_triage: bool | None = None
    enable_experiment_runner: bool | None = None
    parallel_allowed_command_prefixes: list[str] | None = None
    replication_phase: str | None = None
    replication_phase_a_scope: str | None = None
    replication_phase_b_scope: str | None = None
    replication_fidelity: str | None = None
    experiment_runner: ExperimentRunnerPatch | None = None
    quality_gates: QualityGatesPatch | None = None
    #: Replaces the full ``hypotheses`` list when present (same shape as ``Mission.hypotheses``).
    hypotheses: list[Hypothesis] | None = None


class RunAgentStepRequest(BaseModel):
    """Body for ``POST .../agent/run-step``."""

    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True


class MemoryCompactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = True


class LoopRequest(BaseModel):
    goal: str = ""
    perplexity_section: str | None = None
    perplexity_extra: str = ""
    include_notion: bool = False
    cursor_prompt: str = ""
    run_meta: bool = True


class DraftPut(BaseModel):
    """Body for ``PUT .../draft``."""

    model_config = ConfigDict(extra="forbid")

    content: str = ""
