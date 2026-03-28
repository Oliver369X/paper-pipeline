"""Google Gemini client for structured JSON brain responses."""

from __future__ import annotations

import json
import os
from typing import Any


def brain_model_id() -> str:
    # Default: Gemini 3.1 Flash-Lite (preview). Doc:
    # https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview
    # "gemini-3.1-flash" sin sufijo no existe en v1beta (404); Flash 3 genérico: gemini-3-flash-preview.
    raw = (os.environ.get("BRAIN_MODEL") or "gemini-3.1-flash-lite-preview").strip()
    aliases = {
        "gemini-3.1-flash": "gemini-3.1-flash-lite-preview",
    }
    return aliases.get(raw, raw)


def api_key() -> str:
    return (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()


def brain_sdk_available() -> bool:
    """True si el paquete ``google-genai`` está instalado (import ``google.genai``)."""

    try:
        from google import genai  # noqa: F401
    except ImportError:
        return False
    return True


def generate_brain_json(*, system_instruction: str, user_text: str) -> dict[str, Any]:
    """Call Gemini with JSON-only output. Raises on missing key, import error, or API error."""

    key = api_key()
    if not key:
        msg = "Set GOOGLE_API_KEY or GEMINI_API_KEY for the brain (Gemini)."
        raise RuntimeError(msg)

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        msg = "Install google-genai: pip install google-genai"
        raise RuntimeError(msg) from exc

    client = genai.Client(api_key=key)
    model = brain_model_id()
    response = client.models.generate_content(
        model=model,
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
        ),
    )
    text = getattr(response, "text", None) or ""
    if not text.strip():
        msg = "Gemini returned empty response"
        raise RuntimeError(msg)
    return json.loads(text)
