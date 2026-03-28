"""RAG chunking (sin red ni BD)."""

from __future__ import annotations

from paper_pipeline.rag.chunking import chunk_text


def test_chunk_text_single_short() -> None:
    assert chunk_text("hola", max_chars=100) == ["hola"]


def test_chunk_text_splits_long_paragraphs() -> None:
    long = "a" * 5000
    parts = chunk_text(long, max_chars=1000)
    assert len(parts) >= 5
    assert all(len(p) <= 1000 for p in parts)


def test_chunk_text_respects_paragraphs() -> None:
    t = "uno.\n\n" + "dos.\n\n" + "tres."
    c = chunk_text(t, max_chars=10)
    assert len(c) >= 1
