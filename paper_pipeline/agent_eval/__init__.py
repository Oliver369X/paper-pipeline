"""Agent evaluation harness (deterministic oracles, no live Perplexity in CI)."""

from __future__ import annotations

from .eval_runner import run_all, scenarios_dir_default
from .schemas import EvalReport

__all__ = ["EvalReport", "run_all", "scenarios_dir_default"]
