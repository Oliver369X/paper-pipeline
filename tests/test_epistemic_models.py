"""Tests for DCA models and YAML round-trip."""

from __future__ import annotations

import io

import yaml

from paper_pipeline.debug.error_classes import MathErrorClass, diagnostic_prompt_fragment_for_class
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


def _sample_dca() -> DomainContextArtifact:
    return DomainContextArtifact(
        topic="Test topic",
        venue_target="ICLR 2027",
        sota_techniques=["technique A", "technique B"],
        mathematical_constraints=[
            MathematicalConstraint(
                formula=r"L = \|x - \hat{x}\|^2",
                plain_english="MSE reconstruction",
                verification_method="unit_test",
                is_hard_constraint=True,
            )
        ],
        known_pitfalls=[
            KnownPitfall(
                description="bad init",
                source_paper="Smith et al.",
                symptom="NaN",
                fix="lower lr",
            )
        ],
        reference_implementations=[
            ReferenceImplementation(
                name="refrepo",
                github_url="https://github.com/x/y",
                key_design_decisions=["modular"],
                what_not_to_copy=["legacy hacks"],
            )
        ],
        compute_requirements=ComputeRequirements(
            estimated_gpu_memory_gb=16.0,
            estimated_training_time_minutes=60.0,
            requires_gpu=True,
            delegate_to_colab=True,
            colab_accelerator="T4",
        ),
        poison_pills=[
            PoisonPill(
                false_claim="False claim",
                reason_it_is_false="Because",
                detection_query="Is this true?",
            )
        ],
        perplexity_sources=["https://example.com/p1"],
        generation_timestamp="2026-01-01T00:00:00",
        dca_version="2.0",
    )


def test_dca_yaml_round_trip() -> None:
    original = _sample_dca()
    buf = io.StringIO()
    yaml.safe_dump(dca_to_yaml_dict(original), buf, allow_unicode=True, default_flow_style=False)
    buf.seek(0)
    loaded = yaml.safe_load(buf.read())
    assert isinstance(loaded, dict)
    restored = dca_from_yaml_dict(loaded)
    assert restored.topic == original.topic
    assert restored.sota_techniques == original.sota_techniques
    assert len(restored.mathematical_constraints) == 1
    assert restored.mathematical_constraints[0].formula == original.mathematical_constraints[0].formula
    assert restored.known_pitfalls[0].fix == original.known_pitfalls[0].fix
    assert restored.compute_requirements.delegate_to_colab == original.compute_requirements.delegate_to_colab
    assert restored.poison_pills[0].false_claim == original.poison_pills[0].false_claim


def test_every_math_error_class_has_diagnostic_prompt() -> None:
    for cls in MathErrorClass:
        text = diagnostic_prompt_fragment_for_class(cls)
        assert isinstance(text, str)
        assert len(text) > 10
