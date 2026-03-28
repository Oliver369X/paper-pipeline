"""Epistemic layer: Domain Context Artifact (DCA) and injection."""

from __future__ import annotations

from paper_pipeline.epistemic.injector import EpistemicInjector
from paper_pipeline.epistemic.models import (
    ComputeRequirements,
    DomainContextArtifact,
    KnownPitfall,
    MathematicalConstraint,
    PoisonPill,
    ReferenceImplementation,
    dca_from_yaml_dict,
    dca_to_yaml_dict,
)

__all__ = [
    "ComputeRequirements",
    "DomainContextArtifact",
    "EpistemicInjector",
    "KnownPitfall",
    "MathematicalConstraint",
    "PoisonPill",
    "ReferenceImplementation",
    "dca_from_yaml_dict",
    "dca_to_yaml_dict",
]
