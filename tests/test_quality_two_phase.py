"""Tests for two-phase quality parsing."""

from __future__ import annotations

from paper_pipeline.pipeline.quality_two_phase import parse_stage1_sections


def test_parse_stage1_json() -> None:
    raw = '{"sections": ["related_work", "methodology"]}'
    available = ["related_work", "methodology", "gaps"]
    chosen = parse_stage1_sections(raw, available)
    assert chosen == ["related_work", "methodology"]


def test_parse_stage1_fallback() -> None:
    chosen = parse_stage1_sections("not json", ["a", "b", "c"])
    assert len(chosen) == 2
