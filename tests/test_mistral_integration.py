"""Live Mistral API smoke test."""

from __future__ import annotations

import os

import pytest

from paper_pipeline.integrations.mistral_client import MistralClient


@pytest.mark.integration
def test_mistral_real_one_turn() -> None:
    if not os.environ.get("MISTRAL_API_KEY", "").strip():
        pytest.skip("Define MISTRAL_API_KEY in .env")
    client = MistralClient()
    answer = client.ask_single("Reply with one word: pong")
    assert len(answer.strip()) > 0
