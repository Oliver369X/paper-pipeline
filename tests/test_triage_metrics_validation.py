"""MetricsBundle validation before triage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.evidence.metrics_io import load_and_validate_metrics
from paper_pipeline.hypervisor.triage import run_triage_for_mission
from paper_pipeline.mission import Mission


def _minimal_mission(out: Path) -> Mission:
    md = out / "mission.md"
    md.write_text(
        "---\n"
        "topic: t\n"
        "paper_target: p\n"
        f"output_dir: {out / 'outputs'}\n"
        "sections_needed: [gaps]\n"
        "---\n",
        encoding="utf-8",
    )
    return Mission(
        topic="t",
        paper_target="p",
        sections_needed=["gaps"],
        output_dir=str(out / "outputs"),
    )


def test_load_and_validate_metrics_valid(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "exit_code": 0,
                "main": 0.9,
                "baseline": 0.5,
                "coverage": 0.8,
                "math_checks": "PASS",
            },
        ),
        encoding="utf-8",
    )
    bundle, errs = load_and_validate_metrics(p)
    assert bundle is not None
    assert errs == []
    assert bundle.main == 0.9


def test_load_and_validate_metrics_invalid_coverage(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(
        json.dumps({"exit_code": 0, "main": 0.5, "coverage": 1.5}),
        encoding="utf-8",
    )
    bundle, errs = load_and_validate_metrics(p)
    assert bundle is None
    assert errs


def test_load_and_validate_metrics_wrong_type(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps({"exit_code": "bad", "main": 1.0}), encoding="utf-8")
    bundle, errs = load_and_validate_metrics(p)
    assert bundle is None
    assert errs


def test_legacy_without_schema_version_defaults(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 0.7,
                "baseline": 0.5,
                "coverage": 0.6,
                "math_checks": "PASS",
            },
        ),
        encoding="utf-8",
    )
    bundle, errs = load_and_validate_metrics(p)
    assert bundle is not None
    assert errs == []
    assert bundle.schema_version == 1


def test_run_triage_invalid_metrics_tier_zero(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    m = _minimal_mission(tmp_path)
    mp = out / "metrics.json"
    mp.write_text(json.dumps({"coverage": 2.0}), encoding="utf-8")
    rep = run_triage_for_mission(m, out)
    assert rep is not None
    assert rep.tier == 0
    assert rep.label == "invalid_metrics"
    tr = json.loads((out / "triage" / "triage_report.json").read_text(encoding="utf-8"))
    assert "metrics_validation_errors" in tr
    assert tr["metrics_validation_errors"]


def test_run_triage_no_tier_three_if_metrics_invalid(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    m = _minimal_mission(tmp_path)
    mp = out / "metrics.json"
    mp.write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 99.0,
                "baseline": 0.0,
                "coverage": 0.9,
                "math_checks": "PASS",
                "anomaly_detected": True,
            },
        ),
        encoding="utf-8",
    )
    rep = run_triage_for_mission(m, out)
    assert rep is not None
    assert rep.tier == 3

    mp.write_text(json.dumps({"main": 99.0, "coverage": 9.0}), encoding="utf-8")
    rep2 = run_triage_for_mission(m, out)
    assert rep2 is not None
    assert rep2.tier == 0


def test_relax_metrics_uses_triage_parse_when_bundle_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy JSON: MetricsBundle rejects coverage>1; TriageMetrics accepts → classify."""
    monkeypatch.setenv("PAPER_PIPELINE_RELAX_METRICS", "1")
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    m = _minimal_mission(tmp_path)
    mp = out / "metrics.json"
    mp.write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 0.7,
                "baseline": 0.5,
                "coverage": 1.5,
                "math_checks": "PASS",
            },
        ),
        encoding="utf-8",
    )
    rep = run_triage_for_mission(m, out)
    assert rep is not None
    assert rep.tier != 0
    assert rep.label != "invalid_metrics"
    tr = json.loads((out / "triage" / "triage_report.json").read_text(encoding="utf-8"))
    assert tr.get("metrics_relax_mode") is True
    assert tr.get("metrics_bundle_strict_errors")
