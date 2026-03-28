"""meta_watch module."""

from __future__ import annotations

from pathlib import Path

import paper_pipeline.meta_watch as mw


def test_meta_watch_main() -> None:
    assert callable(mw.main)


def test_is_stop_instruction_detects_stop(tmp_path: Path) -> None:
    n = tmp_path / "outputs" / "next_instruction.md"
    n.parent.mkdir(parents=True)
    n.write_text("STOP: ya no hace falta más.\n", encoding="utf-8")
    assert mw._is_stop_instruction(tmp_path / "outputs") is True


def test_is_stop_instruction_false_when_missing(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    assert mw._is_stop_instruction(out) is False


def test_is_stop_instruction_skips_comments_and_blank(tmp_path: Path) -> None:
    n = tmp_path / "outputs" / "next_instruction.md"
    n.parent.mkdir(parents=True)
    n.write_text("\n<!-- x -->\n\nCONTINUE please\n", encoding="utf-8")
    assert mw._is_stop_instruction(tmp_path / "outputs") is False
