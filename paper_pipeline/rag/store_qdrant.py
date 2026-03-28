"""Qdrant vector storage (optional dependency: qdrant-client)."""

from __future__ import annotations

import hashlib

from .models import RagChunkRecord
from .settings import qdrant_api_key, qdrant_collection, qdrant_url


def _point_id(mission_id: str, source_path: str, chunk_index: int) -> int:
    h = hashlib.sha256(f"{mission_id}\0{source_path}\0{chunk_index}".encode()).digest()
    return int.from_bytes(h[:8], "big", signed=False)


def _client():
    try:
        from qdrant_client import QdrantClient
    except ImportError as exc:
        raise RuntimeError("Install qdrant-client for RAG_BACKEND=qdrant.") from exc
    url = qdrant_url()
    if not url:
        raise RuntimeError("QDRANT_URL is not set for RAG (qdrant backend).")
    key = qdrant_api_key()
    return QdrantClient(url=url, api_key=key or None)


def _ensure_collection(dim: int) -> None:
    from qdrant_client.models import Distance, VectorParams

    client = _client()
    name = qdrant_collection()
    if client.collection_exists(name):
        return
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )


def delete_mission_chunks(_conn: None, mission_id: str, *, dim: int) -> None:
    from qdrant_client.http import models as qm

    _ensure_collection(dim)
    client = _client()
    name = qdrant_collection()
    client.delete(
        collection_name=name,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(
                must=[qm.FieldCondition(key="mission_id", match=qm.MatchValue(value=mission_id))]
            )
        ),
    )


def delete_mission_source(_conn: None, mission_id: str, source_path: str, *, dim: int) -> None:
    from qdrant_client.http import models as qm

    _ensure_collection(dim)
    client = _client()
    name = qdrant_collection()
    client.delete(
        collection_name=name,
        points_selector=qm.FilterSelector(
            filter=qm.Filter(
                must=[
                    qm.FieldCondition(key="mission_id", match=qm.MatchValue(value=mission_id)),
                    qm.FieldCondition(key="source_path", match=qm.MatchValue(value=source_path)),
                ]
            )
        ),
    )


def upsert_chunks(
    _conn: None,
    mission_id: str,
    records: list[tuple[RagChunkRecord, list[float]]],
    *,
    dim: int,
) -> None:
    if not records:
        return
    from qdrant_client.models import PointStruct  # type: ignore[import-untyped]

    _ensure_collection(dim)
    client = _client()
    name = qdrant_collection()
    points = []
    for rec, emb in records:
        pid = _point_id(mission_id, rec.source_path, rec.chunk_index)
        points.append(
            PointStruct(
                id=pid,
                vector=emb,
                payload={
                    "mission_id": mission_id,
                    "source_path": rec.source_path,
                    "chunk_index": rec.chunk_index,
                    "content": rec.content,
                },
            )
        )
    client.upsert(collection_name=name, points=points)


def search(
    _conn: None,
    mission_id: str,
    query_embedding: list[float],
    *,
    k: int,
    dim: int,
) -> list[tuple[str, float]]:
    from qdrant_client.http import models as qm

    _ensure_collection(dim)
    client = _client()
    name = qdrant_collection()
    hits = client.search(
        collection_name=name,
        query_vector=query_embedding,
        limit=k,
        query_filter=qm.Filter(
            must=[qm.FieldCondition(key="mission_id", match=qm.MatchValue(value=mission_id))]
        ),
        with_payload=True,
    )
    out: list[tuple[str, float]] = []
    for h in hits:
        payload = h.payload or {}
        text = str(payload.get("content") or "")
        score = float(getattr(h, "score", 0.0) or 0.0)
        out.append((text, score))
    return out
