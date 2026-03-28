"""SkillOrchestrator -- phase-aware skill and MCP routing for the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from paper_pipeline.debug.error_classes import ESCALATE_TO_PERPLEXITY_SIGNAL


class PipelinePhase(Enum):
    """Ordered phases of a full paper-pipeline run."""

    DOMAIN_ACQUISITION = auto()
    HYPOTHESIS_DESIGN = auto()
    IMPLEMENTATION_PLAN = auto()
    CODE_GENERATION = auto()
    DEBUGGING = auto()
    EVALUATION = auto()
    WEB_PACKAGING = auto()
    DOCUMENTATION = auto()
    HUMAN_REVIEW = auto()


SKILL_PHASE_MAP: dict[PipelinePhase, list[str]] = {
    PipelinePhase.DOMAIN_ACQUISITION: [
        "technical-research",
        "hf-mcp",
        "hugging-face-paper-publisher",
    ],
    PipelinePhase.HYPOTHESIS_DESIGN: [
        "brainstorming",
        "writing-plans",
    ],
    PipelinePhase.IMPLEMENTATION_PLAN: [
        "writing-plans",
        "subagent-driven-development",
        "dispatching-parallel-agents",
    ],
    PipelinePhase.CODE_GENERATION: [
        "test-driven-development",
        "executing-plans",
        "hugging-face-model-trainer",
        "gradio",
    ],
    PipelinePhase.DEBUGGING: [
        "systematic-debugging",
        "verification-before-completion",
        "receiving-code-review",
    ],
    PipelinePhase.EVALUATION: [
        "verification-before-completion",
        "hugging-face-evaluation",
        "hugging-face-trackio",
    ],
    PipelinePhase.WEB_PACKAGING: [
        "nextjs",
        "vercel-cli",
        "shadcn",
        "ai-elements",
        "vercel-storage",
        "gradio",
        "hf-cli",
    ],
    PipelinePhase.DOCUMENTATION: [
        "knowledge-capture",
        "tasks-explain-diff",
        "finishing-a-development-branch",
        "using-git-worktrees",
    ],
    PipelinePhase.HUMAN_REVIEW: [],
}

MCP_PHASE_MAP: dict[PipelinePhase, list[str]] = {
    PipelinePhase.DOMAIN_ACQUISITION: [
        "perplexity-web",
        "firecrawl-mcp",
        "github",
    ],
    PipelinePhase.HYPOTHESIS_DESIGN: [
        "perplexity-web",
    ],
    PipelinePhase.IMPLEMENTATION_PLAN: [
        "github",
    ],
    PipelinePhase.CODE_GENERATION: [
        "github",
        "TestSprite",
    ],
    PipelinePhase.DEBUGGING: [
        "perplexity-web",
        "TestSprite",
    ],
    PipelinePhase.EVALUATION: [
        "TestSprite",
        "github",
    ],
    PipelinePhase.WEB_PACKAGING: [
        "plugin-vercel-vercel",
        "plugin-notion-workspace-notion",
        "playwright",
    ],
    PipelinePhase.DOCUMENTATION: [
        "github",
        "plugin-notion-workspace-notion",
    ],
    PipelinePhase.HUMAN_REVIEW: [],
}


@dataclass
class OrchestratorContext:
    """Mutable state carried across pipeline phases."""

    phase: PipelinePhase
    exp_id: str
    domain: str
    consecutive_debug_failures: int = 0
    has_gpu_requirement: bool = False
    is_colab_delegated: bool = False
    previous_phases: list[PipelinePhase] = field(default_factory=list)


class SkillOrchestrator:
    """Resolves which skills and MCP servers are active for a given context."""

    def get_active_skills(self, ctx: OrchestratorContext) -> list[str]:
        """Return the list of skills allowed for the current phase and context.

        Special rules:
        - DEBUGGING with >= 3 consecutive failures appends the Perplexity
          escalation signal so the runner knows to hand off.
        - CODE_GENERATION under Colab delegation adds browser verification
          skills for remote notebook validation.
        - WEB_PACKAGING is blocked (returns []) until EVALUATION has been
          completed in a prior phase.
        """
        if (
            ctx.phase == PipelinePhase.WEB_PACKAGING
            and PipelinePhase.EVALUATION not in ctx.previous_phases
        ):
            return []

        skills = list(SKILL_PHASE_MAP.get(ctx.phase, []))

        if (
            ctx.phase == PipelinePhase.DEBUGGING
            and ctx.consecutive_debug_failures >= 3
        ):
            skills.append(ESCALATE_TO_PERPLEXITY_SIGNAL)

        if ctx.phase == PipelinePhase.CODE_GENERATION and ctx.is_colab_delegated:
            skills.extend(["agent-browser", "agent-browser-verify"])

        return skills

    def get_active_mcps(self, ctx: OrchestratorContext) -> list[str]:
        """Return the list of MCP servers available for the current phase.

        When the experiment is delegated to Colab, ``colab-mcp`` is appended
        regardless of phase.
        """
        mcps = list(MCP_PHASE_MAP.get(ctx.phase, []))
        if ctx.is_colab_delegated:
            mcps.append("colab-mcp")
        return mcps

    def transition_to_phase(
        self,
        ctx: OrchestratorContext,
        new_phase: PipelinePhase,
    ) -> OrchestratorContext:
        """Create a new context for *new_phase*, recording the old phase in history."""
        return OrchestratorContext(
            phase=new_phase,
            exp_id=ctx.exp_id,
            domain=ctx.domain,
            consecutive_debug_failures=ctx.consecutive_debug_failures,
            has_gpu_requirement=ctx.has_gpu_requirement,
            is_colab_delegated=ctx.is_colab_delegated,
            previous_phases=[*ctx.previous_phases, ctx.phase],
        )
