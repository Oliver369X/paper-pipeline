"""Google embeddings via Gemini Developer API or Vertex AI (google-genai)."""

from __future__ import annotations

from paper_pipeline.brain.gemini_client import api_key as brain_api_key

from .settings import (
    embedding_dimensionality,
    embedding_model,
    google_cloud_location,
    google_cloud_project,
    use_vertex_for_embeddings,
)


def _build_genai_client():
    from google import genai

    if use_vertex_for_embeddings():
        project = google_cloud_project()
        if not project:
            raise RuntimeError(
                "RAG_EMBEDDING_USE_VERTEX=1 requires GOOGLE_CLOUD_PROJECT (or GCP_PROJECT).",
            )
        loc = google_cloud_location() or "us-central1"
        return genai.Client(vertexai=True, project=project, location=loc)
    key = brain_api_key()
    if not key:
        raise RuntimeError("Embeddings (ML dev) require GOOGLE_API_KEY or GEMINI_API_KEY.")
    return genai.Client(api_key=key)


def _extract_vectors(response) -> list[list[float]]:
    out: list[list[float]] = []
    embs = getattr(response, "embeddings", None) or []
    for emb in embs:
        vals = getattr(emb, "values", None)
        if vals is not None:
            out.append(list(vals))
    return out


class GoogleEmbeddingClient:
    """google-genai embed_content; batches for Developer API, sequential fallback for Vertex limits."""

    def __init__(self) -> None:
        self._model = embedding_model()
        self.dimension = embedding_dimensionality()
        self._client = _build_genai_client()
        self._vertex = use_vertex_for_embeddings()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        from google.genai import types

        cfg = types.EmbedContentConfig(output_dimensionality=self.dimension)
        results: list[list[float]] = []

        if self._vertex:
            # Vertex embed_content often accepts one content at a time for some models.
            for t in texts:
                resp = self._client.models.embed_content(
                    model=self._model,
                    contents=t,
                    config=cfg,
                )
                vecs = _extract_vectors(resp)
                if not vecs:
                    raise RuntimeError("Embedding response empty (Vertex).")
                results.append(vecs[0])
            return results

        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            resp = self._client.models.embed_content(
                model=self._model,
                contents=batch,
                config=cfg,
            )
            vecs = _extract_vectors(resp)
            if len(vecs) != len(batch):
                raise RuntimeError(
                    f"Embedding count mismatch: got {len(vecs)} for {len(batch)} texts.",
                )
            results.extend(vecs)
        return results


def try_embedding_client() -> GoogleEmbeddingClient | None:
    """Return client if configuration allows embeddings; None if disabled or misconfigured."""

    try:
        return GoogleEmbeddingClient()
    except RuntimeError:
        return None
