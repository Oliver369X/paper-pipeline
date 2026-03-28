"""Tests for integrated loop (directives) without full Perplexity stack."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from paper_pipeline.integrated_loop import execute_directives_from_files
from paper_pipeline.mission import Mission


def test_execute_directives_no_files(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    m = Mission(topic="t", paper_target="p", sections_needed=["gaps"], output_dir=str(out))
    code, rebuilt = execute_directives_from_files(m, out, tmp_path, dry_run=False)
    assert code == 0
    assert rebuilt is False


def test_execute_directives_dry_run(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "cursor_turn.md").write_text("@PERPLEXITY:gaps\n\nHello", encoding="utf-8")
    m = Mission(topic="t", paper_target="p", sections_needed=["gaps"], output_dir=str(out))
    code, rebuilt = execute_directives_from_files(m, out, tmp_path, dry_run=True)
    assert code == 0
    assert rebuilt is False


def test_execute_perplexity_directive_mocked(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "cursor_turn.md").write_text("@PERPLEXITY:gaps\n\nextra", encoding="utf-8")
    m = Mission(
        topic="t",
        paper_target="p",
        sections_needed=["gaps"],
        output_dir=str(out),
        model="best",
        language="en-US",
    )
    mission_path = tmp_path / "mission.md"
    mission_path.write_text(
        f"---\ntopic: t\npaper_target: p\nsections_needed: [gaps]\noutput_dir: {out}\n---\n",
        encoding="utf-8",
    )

    class FakeConv:
        answer = "ok body"
        uuid = "u1"
        read_write_token = None

        def ask(self, *_a, **_k) -> None:
            pass

    class FakePx:
        def __init__(self, *_a, **_k) -> None:
            pass

        def create_conversation(self, _c):
            return FakeConv()

        def close(self) -> None:
            pass

    with patch.dict("os.environ", {"PERPLEXITY_SESSION_TOKEN": "tok"}, clear=False):
        with patch("paper_pipeline.integrated_loop.Perplexity", FakePx):
            code, rebuilt = execute_directives_from_files(m, out, tmp_path, dry_run=False)
    assert code == 0
    assert rebuilt is True
    assert (out / "gaps.md").is_file()
