"""Tests for DRB lite benchmark."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.benchmarks.deep_research_lite import run_benchmark


def test_drb_lite_fixture_mode(tmp_path: Path) -> None:
    report = run_benchmark(tmp_path, draft_path=None)
    assert report["schema_version"] == 1
    assert len(report["questions"]) == 5
    assert (tmp_path / "drb_lite.json").is_file()
