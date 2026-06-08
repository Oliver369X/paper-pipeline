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


@pytest.mark.integration
def test_cursor_sdk_dry_run_if_key_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    if not os.environ.get("CURSOR_API_KEY", "").strip():
        pytest.skip("CURSOR_API_KEY not set")
    try:
        import cursor_sdk  # noqa: F401
    except ImportError:
        pytest.skip("cursor-sdk not installed")

    from paper_pipeline.cursor_cli_runner import run_cursor_cli

    monkeypatch.setenv("CURSOR_AGENT_BACKEND", "sdk")
    out = tmp_path / "outputs"
    out.mkdir()
    code = run_cursor_cli(cwd=tmp_path, output_dir=out, dry_run=True)
    assert code == 0
    log = (out / "cursor_cli.log").read_text(encoding="utf-8")
    assert "backend=sdk" in log
    assert "composer-2.5" in log
