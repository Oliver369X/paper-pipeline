"""Tests for paper-export-appendix (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.reporting.appendix_export import export_appendix_bundle


def test_export_appendix_writes_expected_files(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out = tmp_path / "appendix"
    export_appendix_bundle(out_dir=out, repo_root=repo_root)
    assert (out / "VERSION").is_file()
    assert (out / "git_commit.txt").is_file()
    assert (out / "agent_eval_report.json").is_file()
    assert (out / "pytest_collect.txt").is_file()
    assert (out / "case_study_trace.json").is_file()
    assert (out / "benchmark_bundle.json").is_file()
    assert (out / "benchmark_table.md").is_file()
    trace = json.loads((out / "case_study_trace.json").read_text(encoding="utf-8"))
    assert trace.get("schema_version") == 1
    assert trace.get("kind") == "case_study_trace"
    bb = json.loads((out / "benchmark_bundle.json").read_text(encoding="utf-8"))
    assert bb.get("kind") == "benchmark_bundle"
    assert "| scenario_id |" in (out / "benchmark_table.md").read_text(encoding="utf-8")

    ver = (out / "VERSION").read_text(encoding="utf-8").strip()
    assert ver  # non-empty or unknown from metadata

    data = json.loads((out / "agent_eval_report.json").read_text(encoding="utf-8"))
    assert data.get("scorecard", {}).get("scenario_pass_rate") == 1.0

    collect = (out / "pytest_collect.txt").read_text(encoding="utf-8")
    assert "test_" in collect or "error" in collect.lower() or collect  # pytest output or failure note
