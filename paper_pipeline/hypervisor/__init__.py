"""Hypervisor triage: classify experiment outcomes into tiers (vision_futura)."""

from .triage import (
    TriageMetrics,
    TriageReport,
    classify_triage,
    load_metrics_file,
    write_triage_artifacts,
)

__all__ = [
    "TriageMetrics",
    "TriageReport",
    "classify_triage",
    "load_metrics_file",
    "write_triage_artifacts",
]
