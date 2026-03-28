"""Audit layer: reproducibility notebooks and verification tooling."""

from __future__ import annotations

from paper_pipeline.audit.prove_it import (
    ExperimentMetadata,
    MAKEFILE_TEMPLATE,
    ProveItNotebookGenerator,
    generate_full_audit_package,
)

__all__ = [
    "ExperimentMetadata",
    "MAKEFILE_TEMPLATE",
    "ProveItNotebookGenerator",
    "generate_full_audit_package",
]
