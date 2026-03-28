"""Ejecuta ``outputs/code/run_experiment.py`` con env estándar (sin sandbox OS)."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def run_user_experiment_script(
    script_path: Path,
    mission_root: Path,
    output_dir: Path,
    *,
    timeout_sec: int,
    extra_env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """``python <script>`` con ``cwd=mission_root``. Env: ``PAPER_MISSION_ROOT``, ``PAPER_OUTPUT_DIR``."""

    raw_to = os.environ.get("PAPER_EXPERIMENT_TIMEOUT_SEC", "").strip()
    if raw_to.isdigit():
        timeout_sec = int(raw_to)

    env = os.environ.copy()
    env["PAPER_MISSION_ROOT"] = str(mission_root.resolve())
    env["PAPER_OUTPUT_DIR"] = str(output_dir.resolve())
    env.setdefault("PYTHONUNBUFFERED", "1")
    if extra_env:
        env.update(extra_env)
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(mission_root.resolve()),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        return 124, "", f"timeout after {timeout_sec}s: {exc}"
    logger.info(
        "user experiment script exit=%s script=%s",
        proc.returncode,
        script_path,
    )
    if proc.stdout:
        logger.debug("user script stdout (tail): %s", proc.stdout[-4000:])
    if proc.stderr:
        logger.warning("user script stderr (tail): %s", proc.stderr[-4000:])
    return proc.returncode, proc.stdout, proc.stderr
