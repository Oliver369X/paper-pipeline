"""Explicit pipeline phases (v2 orchestration helper).

The main runner still coordinates I/O; this module names phases and ordering
for documentation, tests, and future extraction.
"""

from __future__ import annotations

from enum import Enum


class PipelinePhaseV2(str, Enum):
    mission_validation = "mission_validation"
    preflight = "preflight"
    perplexity_sections = "perplexity_sections"
    assembly_draft = "assembly_draft"
    claim_extraction = "claim_extraction"
    quality_validation = "quality_validation"
    evidence_packaging = "evidence_packaging"
    triage = "triage"
    notion_sync = "notion_sync"
    cursor_cli = "cursor_cli"
    publication_pack = "publication_pack"
    final_decision = "final_decision"


def default_linear_order() -> list[str]:
    """Ordered phase names for a full run (subset may be skipped)."""

    return [p.value for p in PipelinePhaseV2]
