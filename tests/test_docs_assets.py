"""Sanity checks for documentation assets (P4 architecture figures)."""

from __future__ import annotations

from pathlib import Path


def _assets() -> Path:
    return Path(__file__).resolve().parents[1] / "docs" / "assets"


def test_mermaid_sources_exist_and_non_empty() -> None:
    root = _assets()
    for name in (
        "architecture_overview.mmd",
        "architecture_governance.mmd",
        "case_study_replication_flow.mmd",
    ):
        p = root / name
        assert p.is_file()
        text = p.read_text(encoding="utf-8")
        assert "flowchart" in text
        assert len(text.strip()) > 20
