"""Tests for case_study_trace builder."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_pipeline.reporting.case_study_trace import (
    build_case_study_trace,
    build_minimal_safety_usecase_trace,
)


def test_build_minimal_safety_usecase_trace() -> None:
    repo = Path(__file__).resolve().parents[1]
    t = build_minimal_safety_usecase_trace(repo)
    assert t.get("variant") == "safety_usecase_p2_fixture"
    assert t.get("claims_extracted_count", 0) >= 1


def test_build_case_study_trace_from_sample_mission() -> None:
    repo = Path(__file__).resolve().parents[1]
    out = repo / "data" / "missions" / "4f6715a65f4c" / "outputs"
    if not (out / "run_ledger.json").is_file():
        pytest.skip("sample mission outputs not in workspace")
    t = build_case_study_trace(out)
    assert t.get("mission_id") == "4f6715a65f4c"
    assert isinstance(t.get("phases"), list)
    assert "publish_decision" in t or t.get("ledger_status")
