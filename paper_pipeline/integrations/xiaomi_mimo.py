"""Xiaomi MiMo API client (OpenAI-compatible)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_API_BASE = "https://token-plan-sgp.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"


@dataclass
class MiMoConfig:
    """Configuration for Xiaomi MiMo API."""

    api_key: str = ""
    api_base: str = DEFAULT_API_BASE
    model: str = DEFAULT_MODEL
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: float = 120.0

    @classmethod
    def from_env(cls) -> MiMoConfig:
        """Load config from environment variables."""
        return cls(
            api_key=os.environ.get("XIAOMI_API_KEY", ""),
            api_base=os.environ.get("XIAOMI_API_BASE", DEFAULT_API_BASE),
            model=os.environ.get("XIAOMI_MODEL", DEFAULT_MODEL),
        )


@dataclass
class MiMoMessage:
    """A single message in a MiMo conversation."""

    role: str
    content: str


@dataclass
class MiMoConversation:
    """Manages a conversation with Xiaomi MiMo API."""

    config: MiMoConfig
    messages: list[MiMoMessage] = field(default_factory=list)
    _client: httpx.Client | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.api_base,
                timeout=self.config.timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
            )

    def ask(self, prompt: str) -> str:
        """Send a prompt and get response."""
        self.messages.append(MiMoMessage(role="user", content=prompt))

        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in self.messages],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        try:
            response = self._client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            assistant_message = data["choices"][0]["message"]["content"]
            self.messages.append(MiMoMessage(role="assistant", content=assistant_message))

            return assistant_message

        except httpx.HTTPStatusError as exc:
            logger.error("MiMo API error: %s - %s", exc.response.status_code, exc.response.text)
            print(f"Error detail: {exc.response.text}")
            raise
        except Exception as exc:
            logger.error("MiMo API request failed: %s", exc)
            raise

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


class MiMoClient:
    """Client for Xiaomi MiMo API."""

    def __init__(self, config: MiMoConfig | None = None) -> None:
        if config is None:
            config = MiMoConfig.from_env()
        self.config = config

        if not self.config.api_key:
            raise ValueError("XIAOMI_API_KEY is not set")

    def create_conversation(self) -> MiMoConversation:
        """Create a new conversation."""
        return MiMoConversation(config=self.config)

    def ask_single(self, prompt: str) -> str:
        """Send a single prompt and get response (no conversation history)."""
        conversation = self.create_conversation()
        try:
            return conversation.ask(prompt)
        finally:
            conversation.close()
