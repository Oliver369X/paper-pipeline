"""Domain Context Artifact (DCA) — structured SOTA context before code generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MathematicalConstraint:
    """A verifiable mathematical constraint the implementation must satisfy."""

    formula: str
    plain_english: str
    verification_method: str  # "sympy", "unit_test", "empirical_benchmark"
    is_hard_constraint: bool


@dataclass
class KnownPitfall:
    """Documented failure mode from literature."""

    description: str
    source_paper: str
    symptom: str
    fix: str


@dataclass
class ReferenceImplementation:
    """Reference repo the agent should study."""

    name: str
    github_url: str
    key_design_decisions: list[str]
    what_not_to_copy: list[str]


@dataclass
class ComputeRequirements:
    """GPU / Colab delegation hints."""

    estimated_gpu_memory_gb: float
    estimated_training_time_minutes: float
    requires_gpu: bool
    delegate_to_colab: bool
    colab_accelerator: str


@dataclass
class PoisonPill:
    """Deliberately false claim to detect reward hacking / uncritical acceptance."""

    false_claim: str
    reason_it_is_false: str
    detection_query: str


@dataclass
class DomainContextArtifact:
    """Compiled domain knowledge before any code is written."""

    topic: str
    venue_target: str
    sota_techniques: list[str]
    mathematical_constraints: list[MathematicalConstraint]
    known_pitfalls: list[KnownPitfall]
    reference_implementations: list[ReferenceImplementation]
    compute_requirements: ComputeRequirements
    poison_pills: list[PoisonPill]
    perplexity_sources: list[str]
    generation_timestamp: str = ""
    dca_version: str = "2.0"
    # Raw text blobs from Perplexity (for auditability)
    raw_sota_papers_text: str = ""
    raw_pitfalls_text: str = ""
    raw_repos_text: str = ""
    raw_compute_text: str = ""


def _constraint_from_dict(d: dict[str, Any]) -> MathematicalConstraint:
    return MathematicalConstraint(
        formula=str(d.get("formula", "")),
        plain_english=str(d.get("plain_english", "")),
        verification_method=str(d.get("verification_method", "unit_test")),
        is_hard_constraint=bool(d.get("is_hard_constraint", True)),
    )


def _pitfall_from_dict(d: dict[str, Any]) -> KnownPitfall:
    return KnownPitfall(
        description=str(d.get("description", "")),
        source_paper=str(d.get("source_paper", "")),
        symptom=str(d.get("symptom", "")),
        fix=str(d.get("fix", "")),
    )


def _ref_from_dict(d: dict[str, Any]) -> ReferenceImplementation:
    return ReferenceImplementation(
        name=str(d.get("name", "")),
        github_url=str(d.get("github_url", "")),
        key_design_decisions=list(d.get("key_design_decisions", []) or []),
        what_not_to_copy=list(d.get("what_not_to_copy", []) or []),
    )


def _compute_from_dict(d: dict[str, Any]) -> ComputeRequirements:
    return ComputeRequirements(
        estimated_gpu_memory_gb=float(d.get("estimated_gpu_memory_gb", 8.0)),
        estimated_training_time_minutes=float(d.get("estimated_training_time_minutes", 30.0)),
        requires_gpu=bool(d.get("requires_gpu", True)),
        delegate_to_colab=bool(d.get("delegate_to_colab", False)),
        colab_accelerator=str(d.get("colab_accelerator", "T4")),
    )


def _pill_from_dict(d: dict[str, Any]) -> PoisonPill:
    return PoisonPill(
        false_claim=str(d.get("false_claim", "")),
        reason_it_is_false=str(d.get("reason_it_is_false", "")),
        detection_query=str(d.get("detection_query", "")),
    )


def dca_to_yaml_dict(dca: DomainContextArtifact) -> dict[str, Any]:
    """Serialize DCA to a plain dict suitable for yaml.safe_dump."""
    return asdict(dca)


def dca_from_yaml_dict(data: dict[str, Any]) -> DomainContextArtifact:
    """Reconstruct DCA from YAML-loaded dict."""
    mc = [_constraint_from_dict(x) for x in data.get("mathematical_constraints", []) or []]
    kp = [_pitfall_from_dict(x) for x in data.get("known_pitfalls", []) or []]
    ri = [_ref_from_dict(x) for x in data.get("reference_implementations", []) or []]
    pp = [_pill_from_dict(x) for x in data.get("poison_pills", []) or []]
    cr = _compute_from_dict(data.get("compute_requirements") or {})
    return DomainContextArtifact(
        topic=str(data.get("topic", "")),
        venue_target=str(data.get("venue_target", "arXiv")),
        sota_techniques=list(data.get("sota_techniques", []) or []),
        mathematical_constraints=mc,
        known_pitfalls=kp,
        reference_implementations=ri,
        compute_requirements=cr,
        poison_pills=pp,
        perplexity_sources=list(data.get("perplexity_sources", []) or []),
        generation_timestamp=str(data.get("generation_timestamp", "")),
        dca_version=str(data.get("dca_version", "2.0")),
        raw_sota_papers_text=str(data.get("raw_sota_papers_text", "")),
        raw_pitfalls_text=str(data.get("raw_pitfalls_text", "")),
        raw_repos_text=str(data.get("raw_repos_text", "")),
        raw_compute_text=str(data.get("raw_compute_text", "")),
    )
