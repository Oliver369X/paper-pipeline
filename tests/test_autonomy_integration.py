"""Autonomía + sesión Perplexity: humo de cuota (opcional).

Requiere ``PERPLEXITY_SESSION_TOKEN``. Consume al menos una interacción.

Ejecutar solo:
  pytest tests/test_autonomy_integration.py -m autonomy_integration -q

Misma idea que ``test_perplexity_integration``: valida que los escenarios manuales M1–M4
(``docs/E2E_SCENARIOS.md``) pueden usar una sesión viva.
"""

from __future__ import annotations

import os

import pytest

pytest.importorskip("perplexity_webui_scraper")

from perplexity_webui_scraper import ClientConfig, ConversationConfig, Perplexity


def _token() -> str:
    return os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()


@pytest.mark.autonomy_integration
def test_autonomy_stack_perplexity_session_alive() -> None:
    """Gate de cuota: sin esto, M1/M2/M3 manuales no pueden correr con API real."""
    tok = _token()
    if not tok:
        pytest.skip("Define PERPLEXITY_SESSION_TOKEN para autonomy_integration (ver docs/E2E_SCENARIOS.md)")

    client = Perplexity(tok, config=ClientConfig())
    try:
        conv = client.create_conversation(
            ConversationConfig(
                model="best",
                citation_mode="markdown",
                language="en-US",
            )
        )
        conv.ask("Reply with one word: autonomy-ok")
        answer = (conv.answer or "").strip()
        assert len(answer) > 0, "Perplexity devolvió respuesta vacía (token o sesión)"
    finally:
        client.close()
