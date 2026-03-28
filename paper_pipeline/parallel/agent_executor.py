"""Single-agent subprocess execution inside a worktree (used by orchestrator)."""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import time
from pathlib import Path

from paper_pipeline.parallel.command_safety import validate_agent_command
from paper_pipeline.parallel.git_worktree import GitWorktreeManager
from paper_pipeline.parallel.specs import AgentRunSpec

logger = logging.getLogger(__name__)

_DEFAULT_ALLOWED = ("python", "python3", "pytest", "uv", "pip")


def allowed_command_prefixes() -> tuple[str, ...] | None:
    raw = os.environ.get("PAPER_PIPELINE_PARALLEL_CMD_PREFIXES", "").strip()
    if not raw:
        return _DEFAULT_ALLOWED
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return None
    return tuple(parts)


def _prefixes_from_mission(worktree_path: Path) -> tuple[str, ...] | None:
    """``mission.md`` puede fijar ``parallel_allowed_command_prefixes`` (override del entorno)."""

    mp = worktree_path / "mission.md"
    if not mp.is_file():
        return allowed_command_prefixes()
    try:
        from paper_pipeline.mission import load_mission

        m = load_mission(mp)
    except Exception:
        return allowed_command_prefixes()
    custom = m.parallel_allowed_command_prefixes
    if custom is not None and len(custom) > 0:
        return tuple(str(x).strip() for x in custom if str(x).strip())
    return allowed_command_prefixes()


def apply_triage_if_metrics(worktree_path: Path, spec: AgentRunSpec) -> None:
    """If ``outputs/metrics.json`` exists and mission enables triage, set ``spec.tier_result``."""
    out = worktree_path / "outputs"
    if not (out / "metrics.json").is_file():
        return
    try:
        from paper_pipeline.hypervisor.triage import run_triage_for_mission
        from paper_pipeline.mission import load_mission

        mission = load_mission(worktree_path / "mission.md")
        if not getattr(mission, "enable_hypervisor_triage", False):
            return
        rep = run_triage_for_mission(mission, out)
        if rep is not None:
            spec.tier_result = rep.tier
    except Exception as exc:
        logger.warning("[%s] Worktree triage skipped: %s", spec.exp_id, exc)


async def run_single_agent_in_worktree(
    spec: AgentRunSpec,
    *,
    git_manager: GitWorktreeManager,
    agent_timeout_seconds: int,
    commit_after_each_phase: bool,
    keep_breakthrough_branches: bool,
) -> AgentRunSpec:
    """Create worktree, run command, triage, commit, cleanup."""

    logger.info("[%s] Agent starting.", spec.exp_id)
    worktree_path: Path | None = None
    start_time = time.monotonic()

    try:
        worktree_path = await git_manager.create_worktree(spec)
        spec.worktree_path = worktree_path
        git_manager.inject_mission(spec, worktree_path)

        if spec.command:
            try:
                prefixes = _prefixes_from_mission(worktree_path)
                validate_agent_command(spec.command, allowed_prefixes=prefixes)
            except ValueError as exc:
                spec.error_log = str(exc)
                spec.tier_result = 0
                logger.error("[%s] %s", spec.exp_id, spec.error_log)
                return spec

            process = await asyncio.create_subprocess_exec(
                *spec.command,
                cwd=str(worktree_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=agent_timeout_seconds,
            )
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode,
                    spec.command,
                    output=stdout,
                    stderr=stderr,
                )

        if worktree_path is not None:
            apply_triage_if_metrics(worktree_path, spec)

        if commit_after_each_phase:
            await git_manager.commit_async(
                worktree_path,
                spec.branch_name,
                f"exp({spec.exp_id}): completed "
                f"[{spec.hypothesis[:50]}]",
            )

        elapsed = time.monotonic() - start_time
        logger.info(
            "[%s] Agent completed in %.1fs.", spec.exp_id, elapsed,
        )
        return spec

    except asyncio.TimeoutError:
        spec.error_log = (
            f"TIMEOUT after {agent_timeout_seconds}s"
        )
        spec.tier_result = 0
        logger.error("[%s] %s", spec.exp_id, spec.error_log)
        return spec

    except Exception as exc:
        spec.error_log = str(exc)
        spec.tier_result = 0
        logger.error("[%s] Agent failed: %s", spec.exp_id, exc)
        return spec

    finally:
        if worktree_path and worktree_path.exists():
            keep = (
                spec.tier_result == 3
                and keep_breakthrough_branches
            )
            await git_manager.remove_worktree(
                spec, keep_branch=keep,
            )
