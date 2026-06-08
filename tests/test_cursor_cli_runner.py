"""Tests for Cursor CLI runner (mocked subprocess)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import json
import pytest

from paper_pipeline.constants import ExitCode
from paper_pipeline.cursor_cli_runner import (
    build_cursor_prompt,
    build_followup_cursor_prompt,
    run_cursor_cli,
)
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.mission import Mission


@pytest.fixture(autouse=True)
def force_cli_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_AGENT_BACKEND", "cli")


def test_build_followup_includes_previous_exit_code() -> None:
    p = build_followup_cursor_prompt(
        "BASE TASK",
        attempt=2,
        attempts_total=3,
        prev_exit_code=7,
        prev_stdout="out",
        prev_stderr="err",
    )
    assert "attempt 2 of 3" in p
    assert "**7**" in p or "7" in p
    assert "out" in p and "err" in p
    assert "BASE TASK" in p


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_retries_then_succeeds(
    mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_which.return_value = "/bin/agent"
    mock_run.side_effect = [
        MagicMock(returncode=1, stdout="first out", stderr="first err"),
        MagicMock(returncode=0, stdout="ok", stderr=""),
    ]

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()
    m = Mission(topic="T", paper_target="V", debugging={"cursor_max_attempts": 3})

    code = run_cursor_cli(cwd=cwd, output_dir=out, mission=m, dry_run=False)
    assert code == ExitCode.OK
    assert mock_run.call_count == 2
    second_prompt = mock_run.call_args_list[1][0][0][-1]
    assert "follow-up" in second_prompt.lower() or "Follow-up" in second_prompt
    assert "first out" in second_prompt


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_max_rounds_env_overrides_mission(
    mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    monkeypatch.setenv("CURSOR_CLI_MAX_ROUNDS", "1")
    mock_which.return_value = "/bin/agent"
    mock_run.return_value = MagicMock(returncode=1, stdout="x", stderr="y")

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()
    m = Mission(topic="T", paper_target="V", debugging={"cursor_max_attempts": 5})

    code = run_cursor_cli(cwd=cwd, output_dir=out, mission=m, dry_run=False)
    assert code == ExitCode.ERROR
    mock_run.assert_called_once()


def test_build_cursor_prompt_includes_topic(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    (out / "methodology.md").write_text("m content", encoding="utf-8")
    m = Mission(topic="T", paper_target="V")
    p = build_cursor_prompt(out, m)
    assert "T" in p
    assert "m content" in p


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_success(mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_which.return_value = "/bin/agent"
    mock_run.return_value = MagicMock(returncode=0, stdout="out", stderr="")

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_cli(cwd=cwd, output_dir=out, mission=None, dry_run=False)
    assert code == ExitCode.OK
    mock_run.assert_called_once()
    assert (out / "cursor_cli.log").is_file()
    assert (out / "cursor_turn.md").is_file()
    assert (out / "cursor_cli_diagnostics.json").is_file()
    diag = json.loads((out / "cursor_cli_diagnostics.json").read_text(encoding="utf-8"))
    assert diag.get("exit_code") == 0
    assert "out" in (out / "cursor_turn.md").read_text(encoding="utf-8")


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_extra_args_in_cmd(
    mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    monkeypatch.setenv("CURSOR_AGENT_EXTRA_ARGS", '--model gpt-5 --foo "bar baz"')
    mock_which.return_value = "/bin/agent"
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_cli(cwd=cwd, output_dir=out, mission=None, dry_run=False)
    assert code == ExitCode.OK
    mock_run.assert_called_once()
    cmd = mock_run.call_args[0][0]
    # El runner usa la ruta absoluta que devuelve `which`, no el nombre corto.
    assert Path(cmd[0]).name == "agent"
    assert cmd[1:5] == ["-p", "--force", "--output-format", "text"]
    assert cmd[5:8] == ["--model", "gpt-5", "--foo"]
    assert cmd[8] == "bar baz"
    assert cmd[9].startswith("You are working")


def test_run_cursor_cli_missing_api_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CURSOR_API_KEY", raising=False)
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    out = tmp_path / "o"
    out.mkdir()
    code = run_cursor_cli(cwd=tmp_path, output_dir=out, dry_run=False)
    assert code == ExitCode.CURSOR_CLI_AUTH_ERROR
    assert (out / "cursor_cli_diagnostics.json").is_file()


@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_no_binary(mock_which: MagicMock, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "k")
    mock_which.return_value = None
    out = tmp_path / "o"
    out.mkdir()
    code = run_cursor_cli(cwd=tmp_path, output_dir=out, dry_run=False)
    assert code == ExitCode.CURSOR_CLI_NOT_FOUND


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_dry_run(mock_which: MagicMock, mock_run: MagicMock, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_which.return_value = "/bin/agent"
    out = tmp_path / "o"
    out.mkdir()
    code = run_cursor_cli(cwd=tmp_path, output_dir=out, dry_run=True)
    assert code == ExitCode.OK
    mock_run.assert_not_called()


@patch("paper_pipeline.cursor_cli_runner.subprocess.run")
@patch("paper_pipeline.cursor_cli_runner.shutil.which")
def test_run_cursor_cli_writes_subprocess_done_to_run_log(
    mock_which: MagicMock,
    mock_run: MagicMock,
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_which.return_value = "/bin/agent"
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()
    plog = PipelineLogger(out)

    code = run_cursor_cli(
        cwd=cwd,
        output_dir=out,
        mission=None,
        dry_run=False,
        pipeline_log=plog,
    )
    assert code == ExitCode.OK
    log_lines = (out / "run.log").read_text(encoding="utf-8").strip().splitlines()
    assert log_lines, "run.log should contain structured events"
    last = json.loads(log_lines[-1])
    assert last["event"] == "cursor_cli_subprocess_done"
    assert last["cwd"] == str(cwd.resolve())
    assert last["prompt_chars"] > 0
    assert last["dry_run"] is False
    assert last["timed_out"] is False
    assert last["exit_code"] == 0
    assert "duration_s" in last
