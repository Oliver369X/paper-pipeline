"""Environment-driven RAG configuration."""

from __future__ import annotations

import os


def rag_enabled_for_brain() -> bool:
    v = os.environ.get("BRAIN_RAG_ENABLED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def rag_backend() -> str:
    raw = (os.environ.get("RAG_BACKEND") or "postgres").strip().lower()
    if raw in ("postgres", "pg", "postgresql"):
        return "postgres"
    if raw in ("qdrant",):
        return "qdrant"
    return "postgres"


def database_url() -> str | None:
    u = (os.environ.get("DATABASE_URL") or "").strip()
    return u or None


def qdrant_url() -> str | None:
    u = (os.environ.get("QDRANT_URL") or "").strip()
    return u or None


def qdrant_api_key() -> str | None:
    k = (os.environ.get("QDRANT_API_KEY") or "").strip()
    return k or None


def qdrant_collection() -> str:
    return (os.environ.get("QDRANT_COLLECTION") or "paper_pipeline_rag").strip() or "paper_pipeline_rag"


def embedding_model() -> str:
    return (os.environ.get("RAG_EMBEDDING_MODEL") or "gemini-embedding-001").strip()


def embedding_dimensionality() -> int:
    raw = os.environ.get("RAG_EMBEDDING_DIM", "768").strip()
    try:
        n = int(raw)
    except ValueError:
        return 768
    return max(32, min(n, 3072))


def use_vertex_for_embeddings() -> bool:
    v = os.environ.get("RAG_EMBEDDING_USE_VERTEX", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def google_cloud_project() -> str | None:
    p = (os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or "").strip()
    return p or None


def google_cloud_location() -> str | None:
    loc = (os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1").strip()
    return loc or None


def rag_top_k() -> int:
    raw = os.environ.get("RAG_TOP_K", "8").strip()
    try:
        k = int(raw)
    except ValueError:
        return 8
    return max(1, min(k, 50))


def rag_chunk_max_chars() -> int:
    raw = os.environ.get("RAG_CHUNK_MAX_CHARS", "1800").strip()
    try:
        n = int(raw)
    except ValueError:
        return 1800
    return max(200, min(n, 16_000))


def rag_ingest_max_file_bytes() -> int:
    raw = os.environ.get("RAG_INGEST_MAX_FILE_BYTES", "524288").strip()
    try:
        n = int(raw)
    except ValueError:
        return 524_288
    return max(4096, min(n, 5_000_000))
