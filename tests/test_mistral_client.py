"""Tests for Mistral client (mocked HTTP)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from paper_pipeline.integrations.mistral_client import MistralClient, MistralConfig


@pytest.fixture
def mock_response() -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "choices": [{"message": {"content": "Hello from Mistral"}}],
        "usage": {"total_tokens": 12},
    }
    return resp


def test_mistral_ask_single(mock_response: MagicMock) -> None:
    config = MistralConfig(api_key="test-key", model="mistral-small-latest")
    client = MistralClient(config)

    with patch.object(httpx.Client, "post", return_value=mock_response) as post:
        answer = client.ask_single("ping")
        assert answer == "Hello from Mistral"
        post.assert_called_once()
        payload = post.call_args.kwargs["json"]
        assert payload["model"] == "mistral-small-latest"
        assert payload["messages"][0]["content"] == "ping"


def test_mistral_missing_key() -> None:
    config = MistralConfig(api_key="")
    with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
        MistralClient(config)
