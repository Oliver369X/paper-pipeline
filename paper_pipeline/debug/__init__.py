"""Debugging helpers: math error classification and escalation traces."""

from __future__ import annotations

from paper_pipeline.debug.error_classes import (
    ESCALATE_TO_PERPLEXITY_SIGNAL,
    DebugTrace,
    MathDiagnosis,
    MathErrorClass,
    diagnostic_prompt_fragment_for_class,
)
from paper_pipeline.debug.math_debugger import (
    DebugContextCollector,
    MathDebuggingLoop,
    MathErrorClassifier,
    PerplexityMathConsultant,
)

__all__ = [
    "ESCALATE_TO_PERPLEXITY_SIGNAL",
    "DebugContextCollector",
    "DebugTrace",
    "MathDebuggingLoop",
    "MathDiagnosis",
    "MathErrorClass",
    "MathErrorClassifier",
    "PerplexityMathConsultant",
    "diagnostic_prompt_fragment_for_class",
]
