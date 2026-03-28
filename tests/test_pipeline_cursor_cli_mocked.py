"""Orchestrator con paso Cursor CLI simulado.

Parcheamos ``run_cursor_cli`` (no ``subprocess.run``): en Windows, parchear
``subprocess.run`` afecta todo el módulo ``subprocess`` y rompe p. ej.
``platform.platform()`` durante ``build_evidence_bundle``.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from paper_pipeline.orchestrator import run_pipeline


@pytest.fixture
def fake_perplexity():
    from unittest.mock import patch

    class FakeConversation:
        answer = "ok"

        def ask(self, *_args, **_kwargs) -> None:
            pass

    class FakePerplexity:
        def __init__(self, *_a, **_k) -> None:
            pass

        def create_conversation(self, _cfg) -> FakeConversation:
            return FakeConversation()

        def close(self) -> None:
            pass

    with patch("paper_pipeline.pipeline.runner.Perplexity", FakePerplexity):
        yield


def _fake_cursor_success(**kwargs) -> int:
    output_dir = kwargs["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cursor_turn.md").write_text("ok\n", encoding="utf-8")
    return 0


def _fake_cursor_error(**kwargs) -> int:
    output_dir = kwargs["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cursor_turn.md").write_text("fail\n", encoding="utf-8")
    return 1


@patch("paper_pipeline.cursor_cli_runner.run_cursor_cli")
def test_pipeline_runs_cursor_cli_when_enabled(
    mock_run_cli: MagicMock,
    tmp_path: Path,
    fake_perplexity,
    monkeypatch,
) -> None:
    monkeypatch.setenv("CURSOR_API_KEY", "fake")
    mock_run_cli.side_effect = _fake_cursor_success

    out_abs = (tmp_path / "out_cli").resolve()
    mission = tmp_path / "mission.md"
    mission.write_text(
        f"""---
topic: "Topic"
paper_target: "venue"
sections_needed: [gaps]
max_perplexity_calls: 10
code_needed: true
enable_cursor_cli: true
enable_notion: false
enable_quality_check: false
model: best
output_dir: "{out_abs.as_posix()}"
---
""",
        encoding="utf-8",
    )
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "fake-token-for-test"

    code = run_pipeline(mission, dry_run=False)
    assert code == 0
    assert mock_run_cli.called
    assert (out_abs / "cursor_turn.md").is_file()


@patch("paper_pipeline.cursor_cli_runner.run_cursor_cli")
def test_pipeline_continues_when_cursor_cli_fails_and_optional(
    mock_run_cli: MagicMock,
    tmp_path: Path,
    fake_perplexity,
    monkeypatch,
) -> None:
    """Con cursor_cli_optional (default True), exit 1 del agente no aborta el run."""

    monkeypatch.setenv("CURSOR_API_KEY", "fake")
    mock_run_cli.side_effect = _fake_cursor_error

    out_abs = (tmp_path / "out_cli_fail").resolve()
    mission = tmp_path / "mission.md"
    mission.write_text(
        f"""---
topic: "Topic"
paper_target: "venue"
sections_needed: [gaps]
max_perplexity_calls: 10
code_needed: true
enable_cursor_cli: true
cursor_cli_optional: true
enable_notion: false
enable_quality_check: false
model: best
output_dir: "{out_abs.as_posix()}"
---
""",
        encoding="utf-8",
    )
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "fake-token-for-test"

    code = run_pipeline(mission, dry_run=False)
    assert code == 0
