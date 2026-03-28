"""INTEGRATION_TRANSCRIPT.md append helper."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.integration_transcript import TRANSCRIPT_FILENAME, append_transcript


def test_append_transcript_creates_and_appends(tmp_path: Path) -> None:
    append_transcript(
        tmp_path,
        source="test",
        heading="H1",
        body="cuerpo",
        meta_lines=["k=v"],
    )
    p = tmp_path / TRANSCRIPT_FILENAME
    assert p.is_file()
    t = p.read_text(encoding="utf-8")
    assert "Perplexity + Cursor" in t
    assert "H1" in t
    assert "cuerpo" in t
    assert "k=v" in t

    append_transcript(tmp_path, source="test2", heading="H2", body="dos")
    t2 = p.read_text(encoding="utf-8")
    assert "H2" in t2
    assert "dos" in t2
