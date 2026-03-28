"""Env-driven limits for the brain (Gemini) chat."""

from __future__ import annotations

import os


def brain_max_history_messages() -> int:
    """Tope de turnos enviados a Gemini (cola). Default más alto para hilos 5–10 min."""

    raw = os.environ.get("BRAIN_MAX_HISTORY_MESSAGES", "120").strip()
    try:
        n = int(raw)
    except ValueError:
        return 120
    return max(4, min(n, 500))


def brain_max_brief_chars() -> int:
    raw = os.environ.get("BRAIN_MAX_BRIEF_CHARS", "12000").strip()
    try:
        n = int(raw)
    except ValueError:
        return 12000
    return max(500, min(n, 100_000))


def brain_perplexity_context_max_chars() -> int:
    raw = os.environ.get("BRAIN_PERPLEXITY_CONTEXT_MAX_CHARS", "8000").strip()
    try:
        n = int(raw)
    except ValueError:
        return 8000
    return max(500, min(n, 50_000))


def brain_use_perplexity_context() -> bool:
    v = os.environ.get("BRAIN_USE_PERPLEXITY_CONTEXT", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def brain_force_perplexity_on_arxiv() -> bool:
    """Si el último mensaje del usuario menciona arXiv, intentar siempre un resumen Perplexity (si hay token)."""

    v = os.environ.get("BRAIN_FORCE_PERPLEXITY_ON_ARXIV", "1").strip().lower()
    return v in ("1", "true", "yes", "on")


def brain_max_memory_context_chars() -> int:
    raw = os.environ.get("BRAIN_MAX_MEMORY_CONTEXT_CHARS", "6000").strip()
    try:
        n = int(raw)
    except ValueError:
        return 6000
    return max(0, min(n, 200_000))


def brain_default_run_pipeline_on_apply() -> bool:
    """Si ``run_pipeline`` viene omitido en POST .../brain/apply, usar este default (0/false = compat)."""

    v = os.environ.get("BRAIN_DEFAULT_RUN_PIPELINE_ON_APPLY", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def brain_max_rag_context_chars() -> int:
    raw = os.environ.get("BRAIN_MAX_RAG_CONTEXT_CHARS", "4000").strip()
    try:
        n = int(raw)
    except ValueError:
        return 4000
    return max(0, min(n, 100_000))
