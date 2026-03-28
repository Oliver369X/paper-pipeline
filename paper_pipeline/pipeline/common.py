"""Shared helpers for pipeline phases."""

from __future__ import annotations

from perplexity_webui_scraper import ConversationConfig
from perplexity_webui_scraper.models import MODELS

from paper_pipeline.mission import Mission
from paper_pipeline.state import RunState


def build_conversation_config(mission: Mission) -> ConversationConfig:
    if mission.model not in MODELS:
        available = ", ".join(MODELS)
        msg = f"Unknown model {mission.model!r}. Available: {available}"
        raise ValueError(msg)
    return ConversationConfig(
        model=mission.model,
        citation_mode="markdown",
        language=mission.language,
        save_to_library=mission.save_perplexity_to_library,
    )


def count_prior_perplexity_calls(state: RunState, mission: Mission) -> int:
    n = 0
    for sec in mission.sections_needed:
        if f"perplexity:{sec}" in state.completed_steps:
            n += 1
    if "step:quality_check" in state.completed_steps:
        n += 1
    return n
