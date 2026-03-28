"""Tests for SkillOrchestrator -- phase routing, escalation, and guards."""

from __future__ import annotations

import pytest

from paper_pipeline.debug.error_classes import ESCALATE_TO_PERPLEXITY_SIGNAL
from paper_pipeline.skills.orchestrator import (
    MCP_PHASE_MAP,
    SKILL_PHASE_MAP,
    OrchestratorContext,
    PipelinePhase,
    SkillOrchestrator,
)


@pytest.fixture()
def orchestrator() -> SkillOrchestrator:
    return SkillOrchestrator()


def _base_ctx(phase: PipelinePhase, **overrides) -> OrchestratorContext:
    defaults = dict(exp_id="exp-001", domain="ml-safety")
    defaults.update(overrides)
    return OrchestratorContext(phase=phase, **defaults)


# -- Parametrized: every phase returns the expected skill list ----------------

@pytest.mark.parametrize(
    "phase",
    [p for p in PipelinePhase if p != PipelinePhase.WEB_PACKAGING],
    ids=lambda p: p.name,
)
def test_phase_returns_correct_skills(orchestrator: SkillOrchestrator, phase: PipelinePhase):
    ctx = _base_ctx(phase, previous_phases=[PipelinePhase.EVALUATION])
    result = orchestrator.get_active_skills(ctx)
    assert result == SKILL_PHASE_MAP[phase]


@pytest.mark.parametrize(
    "phase",
    list(PipelinePhase),
    ids=lambda p: p.name,
)
def test_phase_returns_correct_mcps(orchestrator: SkillOrchestrator, phase: PipelinePhase):
    ctx = _base_ctx(phase)
    result = orchestrator.get_active_mcps(ctx)
    assert result == MCP_PHASE_MAP[phase]


# -- Debug escalation --------------------------------------------------------

def test_debug_escalation_below_threshold(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DEBUGGING, consecutive_debug_failures=2)
    skills = orchestrator.get_active_skills(ctx)
    assert ESCALATE_TO_PERPLEXITY_SIGNAL not in skills


def test_debug_escalation_at_threshold(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DEBUGGING, consecutive_debug_failures=3)
    skills = orchestrator.get_active_skills(ctx)
    assert ESCALATE_TO_PERPLEXITY_SIGNAL in skills
    base_skills = SKILL_PHASE_MAP[PipelinePhase.DEBUGGING]
    assert skills[:len(base_skills)] == base_skills


def test_debug_escalation_above_threshold(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DEBUGGING, consecutive_debug_failures=10)
    skills = orchestrator.get_active_skills(ctx)
    assert ESCALATE_TO_PERPLEXITY_SIGNAL in skills


# -- WEB_PACKAGING guard -----------------------------------------------------

def test_web_packaging_blocked_without_evaluation(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.WEB_PACKAGING, previous_phases=[])
    assert orchestrator.get_active_skills(ctx) == []


def test_web_packaging_blocked_with_unrelated_phases(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(
        PipelinePhase.WEB_PACKAGING,
        previous_phases=[PipelinePhase.DOMAIN_ACQUISITION, PipelinePhase.DEBUGGING],
    )
    assert orchestrator.get_active_skills(ctx) == []


def test_web_packaging_allowed_after_evaluation(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(
        PipelinePhase.WEB_PACKAGING,
        previous_phases=[PipelinePhase.EVALUATION],
    )
    assert orchestrator.get_active_skills(ctx) == SKILL_PHASE_MAP[PipelinePhase.WEB_PACKAGING]


# -- Colab delegation --------------------------------------------------------

def test_colab_adds_browser_skills_in_code_generation(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.CODE_GENERATION, is_colab_delegated=True)
    skills = orchestrator.get_active_skills(ctx)
    assert "agent-browser" in skills
    assert "agent-browser-verify" in skills
    base = SKILL_PHASE_MAP[PipelinePhase.CODE_GENERATION]
    assert skills[:len(base)] == base


def test_colab_does_not_add_browser_skills_when_not_delegated(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.CODE_GENERATION, is_colab_delegated=False)
    skills = orchestrator.get_active_skills(ctx)
    assert "agent-browser" not in skills
    assert "agent-browser-verify" not in skills


def test_colab_adds_mcp(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.CODE_GENERATION, is_colab_delegated=True)
    mcps = orchestrator.get_active_mcps(ctx)
    assert "colab-mcp" in mcps


def test_colab_mcp_absent_when_not_delegated(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.CODE_GENERATION, is_colab_delegated=False)
    mcps = orchestrator.get_active_mcps(ctx)
    assert "colab-mcp" not in mcps


# -- Phase transition --------------------------------------------------------

def test_transition_records_history(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DOMAIN_ACQUISITION)
    ctx2 = orchestrator.transition_to_phase(ctx, PipelinePhase.HYPOTHESIS_DESIGN)

    assert ctx2.phase == PipelinePhase.HYPOTHESIS_DESIGN
    assert ctx2.previous_phases == [PipelinePhase.DOMAIN_ACQUISITION]
    assert ctx2.exp_id == ctx.exp_id
    assert ctx2.domain == ctx.domain


def test_transition_accumulates_history(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DOMAIN_ACQUISITION)
    ctx2 = orchestrator.transition_to_phase(ctx, PipelinePhase.HYPOTHESIS_DESIGN)
    ctx3 = orchestrator.transition_to_phase(ctx2, PipelinePhase.IMPLEMENTATION_PLAN)

    assert ctx3.previous_phases == [
        PipelinePhase.DOMAIN_ACQUISITION,
        PipelinePhase.HYPOTHESIS_DESIGN,
    ]


def test_transition_preserves_flags(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(
        PipelinePhase.CODE_GENERATION,
        is_colab_delegated=True,
        has_gpu_requirement=True,
        consecutive_debug_failures=5,
    )
    ctx2 = orchestrator.transition_to_phase(ctx, PipelinePhase.DEBUGGING)

    assert ctx2.is_colab_delegated is True
    assert ctx2.has_gpu_requirement is True
    assert ctx2.consecutive_debug_failures == 5


def test_transition_does_not_mutate_original(orchestrator: SkillOrchestrator):
    ctx = _base_ctx(PipelinePhase.DOMAIN_ACQUISITION)
    original_phases = list(ctx.previous_phases)
    orchestrator.transition_to_phase(ctx, PipelinePhase.HYPOTHESIS_DESIGN)

    assert ctx.previous_phases == original_phases
    assert ctx.phase == PipelinePhase.DOMAIN_ACQUISITION
