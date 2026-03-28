"""Meta-loop con Perplexity simulado."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

from paper_pipeline.meta_loop import STATE_NAME, run_meta_loop


def test_meta_loop_writes_next_instruction(tmp_path: Path) -> None:
    turn = tmp_path / "cursor_turn.md"
    turn.write_text("He creado train.py con un stub.", encoding="utf-8")
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "tok"

    class FakeConv:
        answer = "CONTINUE\n\nSiguiente: añade tests unitarios."
        uuid = "fake-backend-uuid-1"
        read_write_token = "fake-rw"

        def ask(self, *_a, **_k) -> None:
            pass

    class FakePerplexity:
        def __init__(self, *_a, **_k) -> None:
            pass

        def create_conversation(self, _cfg) -> FakeConv:
            return FakeConv()

        def close(self) -> None:
            pass

    with patch("paper_pipeline.meta_loop.Perplexity", FakePerplexity):
        code = run_meta_loop(tmp_path, cursor_turn_file="cursor_turn.md")

    assert code == 0
    next_p = tmp_path / "next_instruction.md"
    assert next_p.is_file()
    text = next_p.read_text(encoding="utf-8")
    assert "@CURSOR" in text
    assert "tests unitarios" in text
    state = json.loads((tmp_path / STATE_NAME).read_text(encoding="utf-8"))
    assert state["round"] == 1


def test_meta_loop_stop_round(tmp_path: Path) -> None:
    turn = tmp_path / "cursor_turn.md"
    turn.write_text("Listo, coverage 90%.", encoding="utf-8")
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "tok"

    class FakeConv:
        answer = "STOP\n\nObjetivo cumplido."
        uuid = None
        read_write_token = None

        def ask(self, *_a, **_k) -> None:
            pass

    class FakePerplexity:
        def __init__(self, *_a, **_k) -> None:
            pass

        def create_conversation(self, _cfg) -> FakeConv:
            return FakeConv()

        def close(self) -> None:
            pass

    with patch("paper_pipeline.meta_loop.Perplexity", FakePerplexity):
        code = run_meta_loop(tmp_path)

    assert code == 1
    assert "STOP" in (tmp_path / "next_instruction.md").read_text(encoding="utf-8")


def test_meta_loop_resumes_perplexity_thread(tmp_path: Path) -> None:
    """Second round uses resume_conversation when state has backend UUID."""

    turn = tmp_path / "cursor_turn.md"
    turn.write_text("Build done.", encoding="utf-8")
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "tok"
    (tmp_path / STATE_NAME).write_text(
        json.dumps(
            {
                "round": 1,
                "perplexity_backend_uuid": "uuid-resume-test",
                "perplexity_read_write_token": "rw-token",
            },
        ),
        encoding="utf-8",
    )

    class FakeConv:
        answer = "CONTINUE\n\nAdd tests."
        uuid = "uuid-resume-test"
        read_write_token = "rw-token"

        def ask(self, *_a, **_k) -> None:
            pass

    class FakePerplexity:
        def __init__(self, *_a, **_k) -> None:
            pass

        def resume_conversation(self, _cfg, *, backend_uuid: str, read_write_token: str | None) -> FakeConv:
            assert backend_uuid == "uuid-resume-test"
            assert read_write_token == "rw-token"
            return FakeConv()

        def create_conversation(self, _cfg) -> FakeConv:
            raise AssertionError("should resume, not create")

        def close(self) -> None:
            pass

    with patch("paper_pipeline.meta_loop.Perplexity", FakePerplexity):
        code = run_meta_loop(tmp_path)

    assert code == 0


def test_meta_loop_max_rounds_skips_perplexity(monkeypatch, tmp_path: Path) -> None:
    """When next round would exceed META_MAX_ROUNDS, do not call Perplexity."""

    turn = tmp_path / "cursor_turn.md"
    turn.write_text("contenido", encoding="utf-8")
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "tok")
    monkeypatch.setenv("META_MAX_ROUNDS", "3")
    (tmp_path / STATE_NAME).write_text('{"round": 3}', encoding="utf-8")

    with patch("paper_pipeline.meta_loop.Perplexity") as mock_pplx:
        code = run_meta_loop(tmp_path)

    assert code == 1
    mock_pplx.assert_not_called()
