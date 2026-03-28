"""High-level RAG: ingest mission markdown and retrieve for brain prompts."""

from __future__ import annotations

import logging
from pathlib import Path

from paper_pipeline.rag.chunking import chunk_text
from paper_pipeline.rag.embeddings import try_embedding_client
from paper_pipeline.rag.models import RagChunkRecord
from paper_pipeline.rag.settings import (
    database_url,
    qdrant_url,
    rag_backend,
    rag_chunk_max_chars,
    rag_enabled_for_brain,
    rag_ingest_max_file_bytes,
    rag_top_k,
)

from .store_postgres import connect as pg_connect
from .store_postgres import delete_mission_chunks as pg_delete_all
from .store_postgres import delete_mission_source as pg_delete_source
from .store_postgres import ensure_schema as pg_ensure_schema
from .store_postgres import search as pg_search
from .store_postgres import upsert_chunks as pg_upsert

logger = logging.getLogger(__name__)

_SKIP_NAMES = {"run.log"}


def _should_ingest_path(p: Path) -> bool:
    if p.suffix.lower() != ".md":
        return False
    if p.name in _SKIP_NAMES:
        return False
    try:
        if p.stat().st_size > rag_ingest_max_file_bytes():
            logger.warning("RAG skip large file: %s", p)
            return False
    except OSError:
        return False
    return True


def _collect_markdown_files(output_dir: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(output_dir.glob("*.md")):
        if _should_ingest_path(p):
            out.append(p)
    return out


def _records_for_files(paths: list[Path], max_c: int) -> list[tuple[RagChunkRecord, str]]:
    """Return (record, plain text for embedding) pairs."""

    pairs: list[tuple[RagChunkRecord, str]] = []
    for fp in paths:
        rel = fp.name
        try:
            raw = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("RAG skip read %s: %s", fp, exc)
            continue
        chunks = chunk_text(raw, max_chars=max_c)
        for i, ch in enumerate(chunks):
            pairs.append((RagChunkRecord(source_path=rel, chunk_index=i, content=ch), ch))
    return pairs


def _ingest_records(
    mission_id: str,
    records_with_vecs: list[tuple[RagChunkRecord, list[float]]],
    *,
    dim: int,
    backend: str,
) -> None:
    if not records_with_vecs:
        return
    if backend == "postgres":
        conn = pg_connect()
        try:
            pg_ensure_schema(conn, dim=dim)
            pg_upsert(conn, mission_id, records_with_vecs)
        finally:
            conn.close()
    else:
        from paper_pipeline.rag import store_qdrant as sq

        sq.upsert_chunks(None, mission_id, records_with_vecs, dim=dim)


def _ingest_core(output_dir: Path, mission_id: str, paths: list[Path], *, full_replace: bool) -> None:
    if not rag_enabled_for_brain():
        return
    emb = try_embedding_client()
    if emb is None:
        logger.warning("RAG ingest skipped: embedding client unavailable.")
        return
    backend = rag_backend()
    if backend == "postgres" and not database_url():
        logger.warning("RAG ingest skipped: DATABASE_URL not set.")
        return
    if backend == "qdrant" and not qdrant_url():
        logger.warning("RAG ingest skipped: QDRANT_URL not set.")
        return

    paths = [p for p in paths if p.is_file() and _should_ingest_path(p)]
    if not paths:
        return

    max_c = rag_chunk_max_chars()
    pre = _records_for_files(paths, max_c)
    if not pre:
        return
    texts = [t for _, t in pre]
    meta = [r for r, _ in pre]
    vectors = emb.embed_texts(texts)
    if len(vectors) != len(meta):
        logger.error("RAG ingest: embedding length mismatch.")
        return
    packed: list[tuple[RagChunkRecord, list[float]]] = list(zip(meta, vectors, strict=True))
    dim = emb.dimension

    if backend == "postgres":
        conn = pg_connect()
        try:
            pg_ensure_schema(conn, dim=dim)
            if full_replace:
                pg_delete_all(conn, mission_id)
            else:
                for p in paths:
                    pg_delete_source(conn, mission_id, p.name)
            pg_upsert(conn, mission_id, packed)
        finally:
            conn.close()
    else:
        from paper_pipeline.rag import store_qdrant as sq

        if full_replace:
            sq.delete_mission_chunks(None, mission_id, dim=dim)
        else:
            for p in paths:
                sq.delete_mission_source(None, mission_id, p.name, dim=dim)
        sq.upsert_chunks(None, mission_id, packed, dim=dim)


def ingest_mission_outputs(output_dir: Path, mission_id: str) -> None:
    """Replace all indexed chunks for *mission_id* with content from ``*.md`` in *output_dir*."""

    files = _collect_markdown_files(output_dir)
    _ingest_core(output_dir, mission_id, files, full_replace=True)


def ingest_brain_brief_only(mission_output_dir: Path, mission_id: str) -> None:
    """Update index for ``brain_brief.md`` only (does not wipe section chunks)."""

    brief = mission_output_dir / "brain_brief.md"
    if not brief.is_file():
        return
    _ingest_core(mission_output_dir, mission_id, [brief], full_replace=False)


def rag_context_for_query(
    mission_id: str,
    query_text: str,
    *,
    max_chars: int,
) -> str | None:
    """Semantic retrieval for brain prompt; returns None if disabled or empty."""

    if not rag_enabled_for_brain():
        return None
    q = (query_text or "").strip()
    if not q:
        return None
    emb = try_embedding_client()
    if emb is None:
        return None
    backend = rag_backend()
    if backend == "postgres" and not database_url():
        return None
    if backend == "qdrant" and not qdrant_url():
        return None

    qv = emb.embed_texts([q])[0]
    k = rag_top_k()
    rows: list[tuple[str, float]] = []
    if backend == "postgres":
        conn = pg_connect()
        try:
            rows = pg_search(conn, mission_id, qv, k=k)
        finally:
            conn.close()
    else:
        from paper_pipeline.rag import store_qdrant as sq

        rows = sq.search(None, mission_id, qv, k=k, dim=emb.dimension)

    if not rows:
        return None
    lines = [f"- (sim {s:.3f}) {t[:800]}" for t, s in rows if t.strip()]
    body = "\n".join(lines)
    if len(body) > max_chars:
        body = body[:max_chars] + "\n[…truncado]"
    return body
