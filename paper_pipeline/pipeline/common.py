"""Shared helpers for pipeline phases."""

from __future__ import annotations

from typing import Any

from perplexity_webui_scraper import ConversationConfig
from perplexity_webui_scraper.models import MODELS

from paper_pipeline.integrations.mistral_client import MistralClient, MistralConfig
from paper_pipeline.integrations.xiaomi_mimo import MiMoClient, MiMoConfig
from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState

OPENAI_COMPAT_PROVIDERS = frozenset({"xiaomi_mimo", "mistral"})

_LEGACY_MODEL_ALIASES: dict[str, str] = {
    "best": "perplexity/best",
    "deep-research": "perplexity/deep-research",
}


def _available_model_ids() -> list[str]:
    if hasattr(MODELS, "list_all"):
        return [m.id for m in MODELS.list_all()]
    if isinstance(MODELS, dict):
        return list(MODELS.keys())
    return []


def _resolve_perplexity_model_id(model_id: str) -> str:
    """Validate and normalize mission model id for ConversationConfig."""
    candidates = [model_id, _LEGACY_MODEL_ALIASES.get(model_id, model_id)]
    if model_id in _LEGACY_MODEL_ALIASES:
        candidates.insert(0, _LEGACY_MODEL_ALIASES[model_id])
    seen: set[str] = set()
    for cid in candidates:
        if cid in seen:
            continue
        seen.add(cid)
        if hasattr(MODELS, "resolve"):
            try:
                MODELS.resolve(cid)
                return cid
            except ValueError:
                pass
        if hasattr(MODELS, "list_all"):
            for m in MODELS.list_all():
                mid = m.id
                if mid == cid or mid.endswith(f"/{cid}"):
                    return mid
        if isinstance(MODELS, dict) and cid in MODELS:
            return cid
    available = ", ".join(_available_model_ids())
    msg = f"Unknown model {model_id!r}. Available: {available}"
    raise ValueError(msg)


def build_conversation_config(mission: Mission) -> ConversationConfig:
    model_id = _resolve_perplexity_model_id(mission.model)
    return ConversationConfig(
        model=model_id,
        citation_mode="markdown",
        language=mission.language,
        save_to_library=mission.save_perplexity_to_library,
    )


def build_mimo_client(mission: Mission) -> MiMoClient:
    """Build MiMo client from mission config."""
    config = MiMoConfig.from_env()
    return MiMoClient(config)


def build_mistral_client(mission: Mission, *, temperature: float | None = None) -> MistralClient:
    """Build Mistral client from mission config and env."""
    config = MistralConfig.from_env(temperature=temperature)
    if mission.model and mission.provider == "mistral":
        config = MistralConfig(
            api_key=config.api_key,
            api_base=config.api_base,
            model=mission.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature if temperature is None else temperature,
            timeout=config.timeout,
        )
    return MistralClient(config)


def section_step_prefix(provider: str) -> str:
    if provider == "mistral":
        return "mistral"
    if provider == "xiaomi_mimo":
        return "mimo"
    return "perplexity"


def count_prior_llm_calls(state: RunState, mission: Mission) -> int:
    prefix = section_step_prefix(mission.provider)
    n = 0
    for sec in mission.sections_needed:
        if f"{prefix}:{sec}" in state.completed_steps:
            n += 1
    if "step:quality_check" in state.completed_steps:
        n += 1
    if "step:research_plan" in state.completed_steps:
        n += 1
    return n


def count_prior_perplexity_calls(state: RunState, mission: Mission) -> int:
    """Backward-compatible alias."""
    return count_prior_llm_calls(state, mission)
