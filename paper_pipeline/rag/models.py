"""Shared RAG record types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RagChunkRecord:
    source_path: str
    chunk_index: int
    content: str
