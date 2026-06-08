"""Tests for citation index."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.pipeline.citation_index import build_citation_index, write_citation_index


def test_citation_index_dedup(tmp_path: Path) -> None:
    s1 = tmp_path / "related_work.md"
    s1.write_text("Paper [1] at https://example.com/a\n", encoding="utf-8")
    s2 = tmp_path / "sota.md"
    s2.write_text("Again https://example.com/a and https://example.com/b\n", encoding="utf-8")
    written = [("related_work", s1), ("sota", s2)]
    index, rewrites = build_citation_index(written)
    write_citation_index(tmp_path, index)
    assert len(index["citations"]) >= 2
    assert "related_work" in rewrites
