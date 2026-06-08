"""Tests for source URL extraction and curation."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.source_curation import extract_urls_from_text, run_source_curation_phase


def test_extract_urls() -> None:
    text = "See https://arxiv.org/abs/2305.04091 and arXiv:2305.04091 also doi 10.1234/example"
    urls = extract_urls_from_text(text)
    assert any("arxiv.org" in u for u in urls)
    assert any("doi.org" in u for u in urls)


def test_curation_no_urls(tmp_path: Path) -> None:
    mission = Mission(topic="t", sections_needed=["gaps"], provider="mistral")
    path = tmp_path / "gaps.md"
    path.write_text("No links here.", encoding="utf-8")
    written = [("gaps", path)]
    plog = MagicMock()
    run_source_curation_phase(mission, tmp_path, written, plog, manifest=None)
    data = json.loads((tmp_path / "sources_curated.json").read_text(encoding="utf-8"))
    assert data["status"] == "no_urls"
