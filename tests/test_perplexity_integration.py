"""Prueba de humo contra la API real de Perplexity (una conversación, un mensaje corto).

Requiere `PERPLEXITY_SESSION_TOKEN` (p. ej. en `.env` o en el entorno).
Consume al menos una interacción de tu cuenta.

Ejecutar solo estas pruebas:
  pytest tests/test_perplexity_integration.py -m integration -q
"""

from __future__ import annotations

import os

import pytest

from perplexity_webui_scraper import ClientConfig, ConversationConfig, Perplexity


def _token() -> str:
    return os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()


@pytest.mark.integration
def test_perplexity_real_one_turn_replies() -> None:
    tok = _token()
    if not tok:
        pytest.skip("Define PERPLEXITY_SESSION_TOKEN (p. ej. copia .env.example → .env)")

    client = Perplexity(tok, config=ClientConfig())
    try:
        conv = client.create_conversation(
            ConversationConfig(
                model="best",
                citation_mode="markdown",
                language="en-US",
            )
        )
        conv.ask("Reply with a single word: pong")
        answer = (conv.answer or "").strip()
        assert len(answer) > 0, "Perplexity devolvió respuesta vacía (revisa token o sesión caducada)"
    finally:
        client.close()
