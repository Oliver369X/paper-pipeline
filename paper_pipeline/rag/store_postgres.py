"""PostgreSQL + pgvector storage."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from .models import RagChunkRecord
from .settings import database_url


def _vec_literal(values: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in values) + "]"


def ensure_schema(conn: psycopg.Connection, *, dim: int) -> None:
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS rag_chunks (
              id BIGSERIAL PRIMARY KEY,
              mission_id TEXT NOT NULL,
              source_path TEXT NOT NULL,
              chunk_index INT NOT NULL,
              content TEXT NOT NULL,
              embedding vector({dim}) NOT NULL,
              UNIQUE (mission_id, source_path, chunk_index)
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS rag_chunks_mission_id_idx ON rag_chunks (mission_id)"
        )
    conn.commit()


def delete_mission_chunks(conn: psycopg.Connection, mission_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM rag_chunks WHERE mission_id = %s", (mission_id,))
    conn.commit()


def delete_mission_source(conn: psycopg.Connection, mission_id: str, source_path: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM rag_chunks WHERE mission_id = %s AND source_path = %s",
            (mission_id, source_path),
        )
    conn.commit()


def upsert_chunks(
    conn: psycopg.Connection,
    mission_id: str,
    records: list[tuple[RagChunkRecord, list[float]]],
) -> None:
    if not records:
        return
    sql = """
    INSERT INTO rag_chunks (mission_id, source_path, chunk_index, content, embedding)
    VALUES (%s, %s, %s, %s, %s::vector)
    ON CONFLICT (mission_id, source_path, chunk_index)
    DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding
    """
    with conn.cursor() as cur:
        for rec, emb in records:
            cur.execute(
                sql,
                (mission_id, rec.source_path, rec.chunk_index, rec.content, _vec_literal(emb)),
            )
    conn.commit()


def search(
    conn: psycopg.Connection,
    mission_id: str,
    query_embedding: list[float],
    *,
    k: int,
) -> list[tuple[str, float]]:
    q = _vec_literal(query_embedding)
    sql = """
    SELECT content, (embedding <=> %s::vector) AS dist
    FROM rag_chunks
    WHERE mission_id = %s
    ORDER BY embedding <=> %s::vector
    LIMIT %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, (q, mission_id, q, k))
        rows = cur.fetchall()
    out: list[tuple[str, float]] = []
    for row in rows:
        dist = float(row["dist"])
        # cosine distance: 0 = identical; similarity ~ 1 - dist for normalized vectors
        sim = max(0.0, 1.0 - dist)
        out.append((str(row["content"]), sim))
    return out


def connect() -> psycopg.Connection:
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set for RAG (postgres backend).")
    return psycopg.connect(url)
