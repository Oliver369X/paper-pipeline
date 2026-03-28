"""Orchestrate Perplexity calls, draft assembly, quality check, Notion sync.

Implementation lives in :mod:`paper_pipeline.pipeline`; this module re-exports for compatibility.
"""

from __future__ import annotations

from paper_pipeline.pipeline import rebuild_draft_from_outputs, run_one_perplexity_section, run_pipeline
from paper_pipeline.pipeline.common import build_conversation_config as _build_conversation_config

__all__ = [
    "_build_conversation_config",
    "rebuild_draft_from_outputs",
    "run_one_perplexity_section",
    "run_pipeline",
]
