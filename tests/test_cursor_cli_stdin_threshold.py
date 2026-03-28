"""Umbral argv vs stdin para Cursor CLI en Windows."""

from __future__ import annotations

import os

import pytest

from paper_pipeline.cursor_cli_runner import _use_stdin_for_prompt


def test_short_prompt_never_stdin_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_CLI_PROMPT_STDIN", "")
    monkeypatch.setattr(os, "name", "nt", raising=False)
    assert _use_stdin_for_prompt("x" * 100) is False


def test_long_prompt_stdin_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_CLI_PROMPT_STDIN", "")
    monkeypatch.setattr(os, "name", "nt", raising=False)
    assert _use_stdin_for_prompt("x" * 8000) is True


def test_force_stdin_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_CLI_PROMPT_STDIN", "1")
    monkeypatch.setattr(os, "name", "posix", raising=False)
    assert _use_stdin_for_prompt("hi") is True


def test_force_argv_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CURSOR_CLI_PROMPT_STDIN", "0")
    monkeypatch.setattr(os, "name", "nt", raising=False)
    assert _use_stdin_for_prompt("x" * 99999) is False
