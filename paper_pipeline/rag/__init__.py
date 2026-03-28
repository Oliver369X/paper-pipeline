"""Optional RAG: Google embeddings + Postgres/pgvector or Qdrant."""

from paper_pipeline.rag.service import ingest_brain_brief_only, ingest_mission_outputs, rag_context_for_query

__all__ = [
    "ingest_brain_brief_only",
    "ingest_mission_outputs",
    "rag_context_for_query",
]
