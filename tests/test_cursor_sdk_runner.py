"""Tests for Cursor SDK runner (mocked cursor_sdk)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from paper_pipeline.constants import ExitCode
from paper_pipeline.cursor_sdk_runner import (
    CURSOR_AGENT_STATE_JSON,
    build_sdk_retry_prompt,
    resolve_cursor_backend,
    resolve_cursor_model,
    run_cursor_via_sdk,
)


@pytest.fixture(autouse=True)
def force_sdk_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_AGENT_BACKEND", "sdk")
    monkeypatch.setenv("CURSOR_AGENT_MODEL", "composer-2.5")


def test_resolve_defaults() -> None:
    assert resolve_cursor_backend() == "sdk"
    assert resolve_cursor_model() == "composer-2.5"


def test_build_sdk_retry_prompt() -> None:
    p = build_sdk_retry_prompt(
        attempt=2,
        attempts_total=3,
        prev_status="error",
        prev_result="out",
        prev_error="err",
    )
    assert "attempt 2 of 3" in p
    assert "out" in p and "err" in p


def _mock_run(*, status: str = "finished", result: str = "done", run_id: str = "run-1") -> MagicMock:
    mock_result = MagicMock()
    mock_result.status = status
    mock_result.result = result
    mock_result.id = run_id
    mock_result.agent_id = "local-agent-1"

    mock_run = MagicMock()
    mock_run.id = run_id
    mock_run.iter_text.return_value = iter([result])
    mock_run.wait.return_value = mock_result
    mock_run.supports.return_value = True
    return mock_run


def _mock_agent(*, agent_id: str = "local-agent-1") -> MagicMock:
    mock_agent = MagicMock()
    mock_agent.agent_id = agent_id
    mock_agent.send.return_value = _mock_run()
    return mock_agent


@patch("cursor_sdk.Client.launch_bridge")
@patch("cursor_sdk.Agent.create")
def test_run_cursor_via_sdk_success(
    mock_create: MagicMock, mock_launch: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_client = MagicMock()
    mock_launch.return_value = mock_client
    mock_create.return_value = _mock_agent()

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_via_sdk(
        cwd=cwd,
        output_dir=out,
        base_body="TASK",
        max_attempts=2,
        timeout_sec=30.0,
        dry_run=False,
        api_key="test-key",
    )
    assert code == ExitCode.OK
    assert mock_create.called
    assert (out / "cursor_cli.log").is_file()
    assert (out / CURSOR_AGENT_STATE_JSON).is_file()
    state = json.loads((out / CURSOR_AGENT_STATE_JSON).read_text(encoding="utf-8"))
    assert state["agent_id"] == "local-agent-1"
    assert state["model"] == "composer-2.5"
    diag = json.loads((out / "cursor_cli_diagnostics.json").read_text(encoding="utf-8"))
    assert diag["backend"] == "sdk"
    assert diag["model"] == "composer-2.5"


@patch("cursor_sdk.Client.launch_bridge")
@patch("cursor_sdk.Agent.create")
def test_run_cursor_via_sdk_dry_run(mock_create: MagicMock, mock_launch: MagicMock, tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_via_sdk(
        cwd=cwd,
        output_dir=out,
        base_body="TASK",
        max_attempts=1,
        timeout_sec=30.0,
        dry_run=True,
        api_key="test-key",
    )
    assert code == ExitCode.OK
    mock_create.assert_not_called()
    mock_launch.assert_not_called()
    log = (out / "cursor_cli.log").read_text(encoding="utf-8")
    assert "backend=sdk" in log
    assert "composer-2.5" in log


@patch("cursor_sdk.Client.launch_bridge")
@patch("cursor_sdk.Agent.create")
def test_run_cursor_via_sdk_retries_then_succeeds(
    mock_create: MagicMock, mock_launch: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    mock_launch.return_value = MagicMock()
    agent = _mock_agent()
    fail_run = _mock_run(status="error", result="failed once", run_id="run-fail")
    ok_run = _mock_run(status="finished", result="ok", run_id="run-ok")
    agent.send.side_effect = [fail_run, ok_run]
    mock_create.return_value = agent

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_via_sdk(
        cwd=cwd,
        output_dir=out,
        base_body="TASK",
        max_attempts=3,
        timeout_sec=30.0,
        dry_run=False,
        api_key="test-key",
    )
    assert code == ExitCode.OK
    assert agent.send.call_count == 2
    second_prompt = agent.send.call_args_list[1][0][0]
    assert "retry" in second_prompt.lower() or "Attempt" in second_prompt


@patch("cursor_sdk.Client.launch_bridge")
@patch("cursor_sdk.Agent.create")
@patch("cursor_sdk.Agent.resume")
def test_run_cursor_via_sdk_resume_fallback_create(
    mock_resume: MagicMock,
    mock_create: MagicMock,
    mock_launch: MagicMock,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from cursor_sdk.errors import UnknownAgentError

    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    monkeypatch.setenv("CURSOR_AGENT_RESUME", "1")

    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()
    cwd_str = str(cwd.resolve())
    (out / CURSOR_AGENT_STATE_JSON).write_text(
        json.dumps(
            {
                "agent_id": "old-agent",
                "backend": "sdk",
                "model": "composer-2.5",
                "cwd": cwd_str,
            }
        ),
        encoding="utf-8",
    )

    mock_resume.side_effect = UnknownAgentError("gone")
    mock_launch.return_value = MagicMock()
    mock_create.return_value = _mock_agent(agent_id="new-agent")

    code = run_cursor_via_sdk(
        cwd=cwd,
        output_dir=out,
        base_body="TASK",
        max_attempts=1,
        timeout_sec=30.0,
        dry_run=False,
        api_key="test-key",
    )
    assert code == ExitCode.OK
    mock_resume.assert_called_once()
    mock_create.assert_called_once()
    state = json.loads((out / CURSOR_AGENT_STATE_JSON).read_text(encoding="utf-8"))
    assert state["agent_id"] == "new-agent"


@patch("cursor_sdk.Client.launch_bridge")
@patch("cursor_sdk.Agent.create")
def test_run_cursor_via_sdk_auth_error(mock_create: MagicMock, mock_launch: MagicMock, tmp_path: Path) -> None:
    from cursor_sdk.errors import AuthenticationError

    mock_launch.side_effect = AuthenticationError("401 unauthorized", status=401)
    out = tmp_path / "outputs"
    out.mkdir()
    cwd = tmp_path / "proj"
    cwd.mkdir()

    code = run_cursor_via_sdk(
        cwd=cwd,
        output_dir=out,
        base_body="TASK",
        max_attempts=1,
        timeout_sec=30.0,
        dry_run=False,
        api_key="bad-key",
    )
    assert code == ExitCode.CURSOR_CLI_AUTH_ERROR
