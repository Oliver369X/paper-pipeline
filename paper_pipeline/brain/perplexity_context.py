"""Optional Perplexity web search summary to enrich brain chat (server-only)."""

from __future__ import annotations

import logging
import os
import re

from paper_pipeline.brain.settings import brain_perplexity_context_max_chars

logger = logging.getLogger(__name__)

_ARXIV_ID = re.compile(r"\b(\d{4}\.\d{4,5})\b")


def user_message_requests_arxiv_verification(user_message: str) -> bool:
    """True si el texto sugiere cita arXiv (URL o id YYMM.NNNNN)."""

    m = (user_message or "").strip()
    if not m:
        return False
    low = m.lower()
    if "arxiv.org" in low or "arxiv:" in low:
        return True
    return _ARXIV_ID.search(m) is not None


def _arxiv_verification_preamble(user_message: str, paper_target: str) -> str:
    """Instrucciones extra para que Perplexity verifique título real; ancla ID frecuentemente confundido."""

    blob = f"{user_message}\n{paper_target}"
    lines = [
        "VERIFICACIÓN WEB (obligatoria): el usuario citó arXiv. Respondé con el **título exacto** como figura en arxiv.org para el ID o URL que mencionó,",
        "autores si constan en la página, y 2–4 frases del problema principal. No inventes nombres de métodos o papers distintos.",
    ]
    if "2410.02159" in blob:
        lines.append(
            "ATENCIÓN: el ID **2410.02159** corresponde al paper **Mitigating Memorization in Language Models** "
            "(no «Differential Transformer» ni otro trabajo). Confirmá en https://arxiv.org/abs/2410.02159 ."
        )
    return "\n".join(lines) + "\n\n"


def fetch_perplexity_context(
    *,
    topic: str,
    user_message: str,
    paper_target: str = "",
    arxiv_verification: bool = False,
) -> str | None:
    """One short Perplexity turn; returns None if unavailable or on error.

    Si ``arxiv_verification`` es True, la pregunta fuerza comprobación de título/ID en la web.
    """

    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    if not token:
        logger.info("Perplexity context skipped: PERPLEXITY_SESSION_TOKEN missing")
        return None

    max_chars = brain_perplexity_context_max_chars()
    try:
        from perplexity_webui_scraper import ClientConfig, ConversationConfig, Perplexity
        from perplexity_webui_scraper.models import MODELS
    except ImportError as exc:
        logger.warning("Perplexity client import failed: %s", exc)
        return None

    model = "best" if "best" in MODELS else MODELS[0]
    pt = paper_target.strip()
    paper_line = (
        f"\nPaper / objetivo explícito (arXiv, DOI o título): {pt[:1500]}\n"
        if pt
        else ""
    )
    intro = (
        _arxiv_verification_preamble(user_message, paper_target)
        if arxiv_verification
        else (
            "Resumen breve: línea de investigación, trabajos relacionados y huecos para replicar o extender "
            "(sin inventar cifras empíricas ni resultados no citados). "
            "Si hay paper objetivo, enlazá la pregunta a ese trabajo y a la literatura vecina.\n"
        )
    )
    query = (
        f"{intro}"
        f"Tema / misión: {topic.strip()[:2000]}"
        f"{paper_line}\n\n"
        f"Pregunta o intención del usuario: {user_message.strip()[:2000]}"
    )
    try:
        client = Perplexity(token, config=ClientConfig())
        cfg = ConversationConfig(
            model=model,
            citation_mode="markdown",
            language="es-ES",
            save_to_library=True,
        )
        conversation = client.create_conversation(cfg)
        conversation.ask(query)
        answer = conversation.answer or ""
    except Exception:
        logger.exception("Perplexity context call failed")
        return None

    text = answer.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[…truncado por BRAIN_PERPLEXITY_CONTEXT_MAX_CHARS]"
    return text or None
