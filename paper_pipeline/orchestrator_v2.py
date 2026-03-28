"""V2 orchestrator wrapper -- opt-in epistemic injection and degradation monitoring.

This module wraps the existing ``run_pipeline`` without modifying it.  Each v2
feature is guarded by a flag on the Mission model and by a try/except so that a
failure in any v2 subsystem never crashes the core pipeline.
"""

from __future__ import annotations

import hashlib
import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from .agent.goal_selection import update_goal_selection_artifacts
from .agent.research_memory import append_research_memory
from .agent.objective_state import update_objective_artifacts
from .constants import ExitCode
from .mission import Mission, load_mission
from .orchestrator import run_pipeline

logger = logging.getLogger(__name__)


def _run_epistemic_injection(mission: Mission, output_dir: Path) -> None:
    """Build a Domain Context Artifact and persist it to *output_dir*."""
    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    if not token:
        logger.warning("Epistemic injection skipped: PERPLEXITY_SESSION_TOKEN not set")
        return

    from .epistemic.injector import EpistemicInjector

    injector = EpistemicInjector(
        token,
        output_dir,
        model=mission.model,
        language=mission.language,
    )
    try:
        dca = injector.build_domain_context(mission.topic, mission.paper_target)
        prompt_text = injector.generate_cursor_system_prompt(dca)
        prompt_path = output_dir / "epistemic_system_prompt.md"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        logger.info(
            "Epistemic injection complete: %d SOTA techniques, DCA at %s",
            len(dca.sota_techniques),
            output_dir / "domain_context.yaml",
        )
    finally:
        injector.close()


def _run_degradation_check(mission: Mission, output_dir: Path) -> None:
    """Evaluate the draft paper for quality degradation."""
    from .validation.degradation import DegradationMonitor

    draft_path = output_dir / "draft_paper.md"
    if not draft_path.is_file():
        logger.warning("Degradation check skipped: %s not found", draft_path)
        return

    draft_text = draft_path.read_text(encoding="utf-8")
    monitor = DegradationMonitor(anchor_text=mission.topic)
    metrics = monitor.evaluate(draft_text, history=[], check_urls=False)

    logger.info(
        "Degradation metrics -- density=%.3f  repetition=%.3f  drift=%.3f  citations=%.3f",
        metrics.information_density,
        metrics.self_repetition,
        metrics.topic_drift,
        metrics.citation_ratio,
    )

    if monitor.is_degraded(metrics):
        logger.warning(
            "Draft shows signs of degradation (density=%.3f, repetition=%.3f, drift=%.3f). "
            "Consider regenerating affected sections.",
            metrics.information_density,
            metrics.self_repetition,
            metrics.topic_drift,
        )


def _run_skill_orchestrator_manifest(mission: Mission, output_dir: Path) -> None:
    """Write a YAML manifest of skills/MCP per pipeline phase (no network calls).

    Safe artefact for humans and Cursor: lists which skills and MCP servers the
    :class:`~paper_pipeline.skills.orchestrator.SkillOrchestrator` associates
    with each :class:`~paper_pipeline.skills.orchestrator.PipelinePhase`.
    """
    from .skills.orchestrator import (
        OrchestratorContext,
        PipelinePhase,
        SkillOrchestrator,
    )

    orch = SkillOrchestrator()
    exp_id = hashlib.sha256(mission.topic.encode("utf-8")).hexdigest()[:12]
    domain = mission.topic.strip() or "unknown-domain"

    manifest: dict[str, Any] = {
        "version": 1,
        "experiment_id": exp_id,
        "domain_preview": domain[:500] + ("…" if len(domain) > 500 else ""),
        "phases": {},
    }

    for phase in PipelinePhase:
        ctx = OrchestratorContext(phase=phase, exp_id=exp_id, domain=domain)
        entry: dict[str, Any] = {
            "skills": orch.get_active_skills(ctx),
            "mcps": orch.get_active_mcps(ctx),
        }
        if phase == PipelinePhase.WEB_PACKAGING:
            ctx_unlocked = OrchestratorContext(
                phase=phase,
                exp_id=exp_id,
                domain=domain,
                previous_phases=[PipelinePhase.EVALUATION],
            )
            entry["skills_after_evaluation_phase"] = orch.get_active_skills(ctx_unlocked)
        if mission.compute.colab_mcp_enabled and phase == PipelinePhase.CODE_GENERATION:
            ctx_colab = OrchestratorContext(
                phase=phase,
                exp_id=exp_id,
                domain=domain,
                is_colab_delegated=True,
            )
            entry["skills_colab_delegated"] = orch.get_active_skills(ctx_colab)
            entry["mcps_colab"] = orch.get_active_mcps(ctx_colab)

        manifest["phases"][phase.name] = entry

    path = output_dir / "skill_orchestrator_manifest.yaml"
    path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    logger.info("Skill orchestrator manifest written to %s", path)


def run_pipeline_v2(
    mission_path: Path,
    *,
    dry_run: bool = False,
    event_sink: Callable[[dict], None] | None = None,
) -> int:
    """Run the paper pipeline with optional v2 features.

    This is a thin wrapper around :func:`run_pipeline`.  It inspects the
    mission's ``enable_epistemic_injection``, ``enable_degradation_monitor``,
    ``enable_skill_orchestrator``, and ``enable_hypervisor_triage`` flags and,
    when enabled, runs the
    corresponding subsystem *around* the core pipeline.  Any failure in a v2
    feature is logged as a warning and does **not** abort the pipeline.

    Args:
        mission_path: Path to the ``mission.md`` file.
        dry_run: If True, skip real Perplexity calls (passed through to v1).
        event_sink: Optional callback for pipeline events.

    Returns:
        Process exit code (0 on success).
    """
    try:
        mission = load_mission(mission_path)
    except (OSError, ValueError) as exc:
        logger.error("Invalid mission file: %s", exc)
        return ExitCode.ERROR

    output_dir = Path(mission.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    enable_epistemic = getattr(mission, "enable_epistemic_injection", False)
    enable_degradation = getattr(mission, "enable_degradation_monitor", False)
    enable_skills = getattr(mission, "enable_skill_orchestrator", False)

    # --- Pre-pipeline: skill / MCP routing manifest (pure, no network) ---
    if enable_skills:
        try:
            _run_skill_orchestrator_manifest(mission, output_dir)
        except Exception:
            logger.warning("Skill orchestrator manifest failed; continuing pipeline", exc_info=True)

    # --- Pre-pipeline: epistemic injection ---
    if enable_epistemic and not dry_run:
        try:
            _run_epistemic_injection(mission, output_dir)
        except Exception:
            logger.warning("Epistemic injection failed; continuing pipeline", exc_info=True)

    # --- Core pipeline (v1) ---
    exit_code = run_pipeline(mission_path, dry_run=dry_run, event_sink=event_sink)

    # --- Post-pipeline: degradation monitoring ---
    if enable_degradation and not dry_run:
        try:
            _run_degradation_check(mission, output_dir)
        except Exception:
            logger.warning("Degradation check failed; ignoring", exc_info=True)

    # --- Post-pipeline: hypervisor triage (tier + artifacts if metrics.json exists) ---
    enable_hypervisor = getattr(mission, "enable_hypervisor_triage", False)
    if enable_hypervisor and not dry_run:
        try:
            from .agent.safety import SafetyContext, SafetyController
            from .agent.safety_trace import append_safety_trace
            from .hypervisor.triage import run_triage_for_mission
            from .ledger.writer import merge_ledger_after_triage
            from .publication.publish_manager import write_publish_decision

            rep = run_triage_for_mission(mission, output_dir)
            if rep is not None:
                ctx = SafetyContext(
                    candidate_action="post_triage_review",
                    triage_tier=rep.tier,
                    source_artifacts=["triage/triage_report.json"],
                )
                append_safety_trace(output_dir, ctx, SafetyController().evaluate(ctx))
            write_publish_decision(output_dir, mission)
            merge_ledger_after_triage(output_dir)
            update_objective_artifacts(output_dir, candidate_action_family="post_hypervisor")
            append_research_memory(
                output_dir,
                kind="run_consolidation",
                summary="Consolidación post-hypervisor en orquestador v2",
                source_artifacts=[
                    "triage/triage_report.json",
                    "publication/publish_decision.json",
                    "run_ledger.json",
                    "objective_state.json",
                ],
                payload={"phase": "post_hypervisor"},
                tags=["run", "hypervisor"],
                confidence=0.85,
            )
            update_goal_selection_artifacts(output_dir)
        except Exception:
            logger.warning("Hypervisor triage failed; ignoring", exc_info=True)

    return exit_code
