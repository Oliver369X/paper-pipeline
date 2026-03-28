"""CLI entry tests — no unittest.mock.patch on pipeline functions (see plan)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from paper_pipeline import __main__ as cli
from paper_pipeline.orchestrator import run_pipeline
from paper_pipeline.orchestrator_v2 import run_pipeline_v2

from test_orchestrator_v2 import _write_mission


def test_build_parser_defaults() -> None:
    args = cli.build_parser().parse_args([])
    assert args.mission == Path("mission.md")
    assert args.dry_run is False
    assert args.v2 is False


def test_build_parser_v2_and_dry_run() -> None:
    args = cli.build_parser().parse_args(["--v2", "--dry-run", "foo.md"])
    assert args.mission == Path("foo.md")
    assert args.dry_run is True
    assert args.v2 is True


def test_build_parser_mission_after_flags() -> None:
    args = cli.build_parser().parse_args(["--dry-run", "bar.md", "--v2"])
    assert args.mission == Path("bar.md")
    assert args.dry_run is True
    assert args.v2 is True


def test_select_runner_identity() -> None:
    assert cli._select_runner(False) is run_pipeline
    assert cli._select_runner(True) is run_pipeline_v2


def test_main_dry_run_v2_exits_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "fake-token-for-cli-test")
    mission = _write_mission(tmp_path)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        cli.main([str(mission), "--dry-run", "--v2"])
    assert exc.value.code == 0


def test_main_dry_run_v1_exits_ok(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "fake-token-for-cli-test")
    mission = _write_mission(tmp_path)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        cli.main([str(mission), "--dry-run"])
    assert exc.value.code == 0


def test_subprocess_module_invocation_v2_dry_run(tmp_path: Path) -> None:
    """Smoke: separate process resolves -m paper_pipeline with --v2."""
    mission = _write_mission(tmp_path)
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": str(repo_root), "PERPLEXITY_SESSION_TOKEN": "fake-token"}
    proc = subprocess.run(
        [sys.executable, "-m", "paper_pipeline", str(mission), "--dry-run", "--v2"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
