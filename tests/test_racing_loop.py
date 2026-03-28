"""Tests para paper-racing-loop (sin Cursor real)."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_pipeline.racing_prompts import GAME_REL, improvement_loop_prompt, round_prompts


def test_game_path_constant() -> None:
    assert GAME_REL == "outputs/code/X"


def test_six_rounds_by_default() -> None:
    assert len(round_prompts()) == 6


def test_mission_file_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    m = root / "missions" / "racing_game_3d" / "mission.md"
    assert m.is_file()


def test_improvement_prompt_contains_estado() -> None:
    title, body = improvement_loop_prompt(iteration=1, max_iter=3)
    assert "Mejora continua" in title
    assert "ESTADO:" in body
