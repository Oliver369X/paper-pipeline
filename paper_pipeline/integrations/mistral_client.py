"""Mistral API client (OpenAI-compatible chat completions)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_API_BASE = "https://api.mistral.ai/v1"
DEFAULT_MODEL = "mistral-large-latest"


@dataclass
class MistralConfig:
    """Configuration for Mistral API."""

    api_key: str = ""
    api_base: str = DEFAULT_API_BASE
    model: str = DEFAULT_MODEL
    max_tokens: int = 4096
    temperature: float = 0.3
    timeout: float = 120.0

    @classmethod
    def from_env(cls, *, temperature: float | None = None) -> MistralConfig:
        """Load config from environment variables."""
        temp_raw = os.environ.get("MISTRAL_TEMPERATURE", "0.3")
        try:
            temp = float(temp_raw)
        except ValueError:
            temp = 0.3
        if temperature is not None:
            temp = temperature
        try:
            max_tokens = int(os.environ.get("MISTRAL_MAX_TOKENS", "4096"))
        except ValueError:
            max_tokens = 4096
        try:
            timeout = float(os.environ.get("MISTRAL_TIMEOUT_SEC", "120"))
        except ValueError:
            timeout = 120.0
        return cls(
            api_key=os.environ.get("MISTRAL_API_KEY", ""),
            api_base=os.environ.get("MISTRAL_API_BASE", DEFAULT_API_BASE),
            model=os.environ.get("MISTRAL_MODEL", DEFAULT_MODEL),
            max_tokens=max_tokens,
            temperature=temp,
            timeout=timeout,
        )


@dataclass
class MistralMessage:
    """A single message in a Mistral conversation."""

    role: str
    content: str


@dataclass
class MistralConversation:
    """Manages a conversation with Mistral API."""

    config: MistralConfig
    messages: list[MistralMessage] = field(default_factory=list)
    _client: httpx.Client | None = field(default=None, repr=False)
    last_usage: dict[str, Any] | None = field(default=None, repr=False)

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
        self.messages.append(MistralMessage(role="user", content=prompt))

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
            self.messages.append(MistralMessage(role="assistant", content=assistant_message))
            usage = data.get("usage")
            self.last_usage = usage if isinstance(usage, dict) else None

            return assistant_message

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Mistral API error: %s - %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except Exception as exc:
            logger.error("Mistral API request failed: %s", exc)
            raise

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None


class MistralClient:
    """Client for Mistral API."""

    def __init__(self, config: MistralConfig | None = None) -> None:
        if config is None:
            config = MistralConfig.from_env()
        self.config = config

        if not self.config.api_key:
            raise ValueError("MISTRAL_API_KEY is not set")

    def create_conversation(self, *, temperature: float | None = None) -> MistralConversation:
        """Create a new conversation."""
        cfg = self.config
        if temperature is not None:
            cfg = MistralConfig(
                api_key=cfg.api_key,
                api_base=cfg.api_base,
                model=cfg.model,
                max_tokens=cfg.max_tokens,
                temperature=temperature,
                timeout=cfg.timeout,
            )
        return MistralConversation(config=cfg)

    def ask_single(self, prompt: str, *, temperature: float | None = None) -> str:
        """Send a single prompt and get response (no conversation history)."""
        conversation = self.create_conversation(temperature=temperature)
        try:
            return conversation.ask(prompt)
        finally:
            conversation.close()
