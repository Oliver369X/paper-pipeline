"""Invalidación de pasos reanudables tras fallos críticos (experimento / CLI)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path

from paper_pipeline.mission import ExperimentRunnerConfig, Mission
from paper_pipeline.state import RunState

logger = logging.getLogger(__name__)


def invalidate_resume_after_critical_failure(
    state: RunState,
    state_path: Path,
    *,
    cause: str,
) -> None:
    """Quita ``step:quality_check`` del resume; opcionalmente todas las secciones Perplexity (env)."""

    state.completed_steps = [s for s in state.completed_steps if s != "step:quality_check"]
    inv_px = os.environ.get("PAPER_PIPELINE_INVALIDATE_PERPLEXITY_ON_EXP_FAIL", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if inv_px:
        state.completed_steps = [s for s in state.completed_steps if not s.startswith("perplexity:")]
    state.last_critical_failure = cause
    state.save(state_path)


def experiment_runner_config_hash(cfg: ExperimentRunnerConfig) -> str:
    """Hash estable de la sección ``experiment_runner`` de la misión."""

    raw = json.dumps(cfg.model_dump(), sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def invalidate_resume_if_experiment_runner_config_changed(
    mission: Mission,
    state: RunState,
    state_path: Path,
) -> None:
    """Si el bloque ``experiment_runner`` cambió respecto al último run, no reutilizar narrativa Perplexity."""

    if not mission.enable_experiment_runner:
        return
    from paper_pipeline.pipeline.experiment_contracts import strip_empirical_dependent_resume_steps

    new_h = experiment_runner_config_hash(mission.experiment_runner)
    old_h = (state.experiment_runner_config_hash or "").strip()
    if not old_h or new_h == old_h:
        return
    strip_empirical_dependent_resume_steps(state)
    state.save(state_path)
    logger.warning(
        "experiment_runner config hash changed (%s -> %s): invalidated perplexity:* and quality_check",
        old_h,
        new_h,
    )
