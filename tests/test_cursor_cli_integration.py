"""Opcional: comprobar que el binario `agent` existe (requiere instalación Cursor CLI)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def _resolve_agent_executable(agent_bin: str) -> str | None:
    p = Path(agent_bin)
    if p.is_file():
        return str(p.resolve())
    w = shutil.which(agent_bin)
    return w


@pytest.mark.integration
def test_cursor_agent_help_exits_zero_if_installed() -> None:
    if not os.environ.get("CURSOR_API_KEY", "").strip():
        pytest.skip("CURSOR_API_KEY not set")
    agent_bin = os.environ.get("CURSOR_AGENT_BIN", "agent").strip() or "agent"
    resolved = _resolve_agent_executable(agent_bin)
    if not resolved:
        pytest.skip("Cursor CLI not on PATH (install from cursor.com/docs/cli/headless)")
    # Windows: `agent` suele ser agent.cmd; CreateProcess no ejecuta .cmd con argv-list.
    if os.name == "nt" and resolved.lower().endswith((".cmd", ".bat")):
        proc = subprocess.run(
            f'"{resolved}" --help',
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
    else:
        proc = subprocess.run(
            [resolved, "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
