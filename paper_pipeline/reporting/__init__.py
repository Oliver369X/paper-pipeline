"""Reporting helpers: publication-quality figures from ``outputs/metrics.json``."""

from __future__ import annotations

from paper_pipeline.reporting.paper_figures import (
    figure_main_vs_baseline,
    load_metrics_dict,
    sota_claim_paragraph_en,
)

__all__ = [
    "figure_main_vs_baseline",
    "load_metrics_dict",
    "sota_claim_paragraph_en",
]
