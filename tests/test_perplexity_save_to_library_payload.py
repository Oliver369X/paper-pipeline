"""Contract: library-visible threads require SSE params.is_incognito=false (see ConversationConfig)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from perplexity_webui_scraper.config import ConversationConfig
from perplexity_webui_scraper.core import Conversation
from perplexity_webui_scraper.models import MODELS

from paper_pipeline.mission import Mission
from paper_pipeline.orchestrator import _build_conversation_config


@pytest.mark.parametrize(
    ("save_to_library", "expect_incognito"),
    [(True, False), (False, True)],
)
def test_build_payload_is_incognito_matches_save_to_library(
    save_to_library: bool,
    expect_incognito: bool,
) -> None:
    http = MagicMock()
    cfg = ConversationConfig(model="best", save_to_library=save_to_library)
    conv = Conversation(http, cfg)
    model = MODELS["best"]
    payload = conv._build_payload("test query", model, [])
    assert payload["params"]["is_incognito"] is expect_incognito


def test_orchestrator_conversation_config_passes_mission_flag() -> None:
    m_on = Mission(topic="t", paper_target="p", save_perplexity_to_library=True)
    c_on = _build_conversation_config(m_on)
    assert c_on.save_to_library is True

    m_off = Mission(topic="t", paper_target="p", save_perplexity_to_library=False)
    c_off = _build_conversation_config(m_off)
    assert c_off.save_to_library is False
