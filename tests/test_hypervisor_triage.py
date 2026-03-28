"""Unit tests for hypervisor tier classification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.hypervisor.triage import (
    TriageMetrics,
    classify_triage,
    run_triage_for_mission,
    write_triage_artifacts,
)
from paper_pipeline.mission import Mission, QualityGatesConfig


def _mission(**qg) -> Mission:
    q = QualityGatesConfig(**{**{"sota_baseline_value": 0.8, "breakthrough_margin": 0.05, "replication_tolerance": 0.02, "higher_is_better": True}, **qg})
    return Mission(topic="t", paper_target="v", quality_gates=q)


def test_tier_0_exit_code() -> None:
    m = _mission()
    r = classify_triage(TriageMetrics(exit_code=1, main=0.9), m)
    assert r.tier == 0


def test_tier_0_low_coverage() -> None:
    m = _mission()
    r = classify_triage(TriageMetrics(exit_code=0, main=0.9, coverage=0.2), m)
    assert r.tier == 0


def test_tier_3_breakthrough_metric() -> None:
    m = _mission(sota_baseline_value=0.5, breakthrough_margin=0.01)
    r = classify_triage(
        TriageMetrics(exit_code=0, main=0.99, baseline=0.5, coverage=0.9, math_checks="PASS"),
        m,
    )
    assert r.tier == 3
    assert r.label == "breakthrough"


def test_tier_3_anomaly() -> None:
    m = _mission()
    r = classify_triage(
        TriageMetrics(exit_code=0, main=0.5, anomaly_detected=True, coverage=0.9),
        m,
    )
    assert r.tier == 3


def test_tier_1_refuted() -> None:
    m = _mission(sota_baseline_value=0.9, breakthrough_margin=0.05)
    r = classify_triage(
        TriageMetrics(exit_code=0, main=0.3, baseline=0.9, math_checks="PASS", coverage=0.9),
        m,
    )
    assert r.tier == 1
    assert "refuted" in r.label


def test_tier_2_replication_band() -> None:
    m = _mission(sota_baseline_value=0.8, replication_tolerance=0.05)
    r = classify_triage(
        TriageMetrics(exit_code=0, main=0.81, baseline=0.8, coverage=0.9, math_checks="FAIL"),
        m,
    )
    assert r.tier == 2
    assert r.label == "sota_match"


def test_run_triage_writes_json(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 0.95,
                "baseline": 0.5,
                "coverage": 0.9,
                "math_checks": "PASS",
            }
        ),
        encoding="utf-8",
    )
    mission = _mission(sota_baseline_value=0.5, breakthrough_margin=0.01)
    rep = run_triage_for_mission(mission, out)
    assert rep is not None
    assert (out / "triage" / "triage_report.json").is_file()


def test_tier_1_writes_failures_md(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    mission = _mission(sota_baseline_value=0.95, breakthrough_margin=0.01)
    metrics = TriageMetrics(
        exit_code=0,
        main=0.2,
        baseline=0.95,
        coverage=0.9,
        math_checks="PASS",
    )
    report = classify_triage(metrics, mission)
    write_triage_artifacts(out, mission, metrics, report)
    assert report.tier == 1
    assert (out / "triage" / "FAILURES.md").is_file()


def test_webhook_called_on_tier3_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    posted: list[dict] = []

    class _Resp:
        def read(self, n: int = -1) -> bytes:
            return b"ok"

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    def fake_urlopen(req, timeout=0):  # noqa: ANN001
        posted.append(json.loads(req.data.decode("utf-8")))
        return _Resp()

    monkeypatch.setenv("PAPER_PIPELINE_TRIAGE_WEBHOOK_URL", "https://example.com/hook")
    monkeypatch.setattr("paper_pipeline.hypervisor.triage.urlopen", fake_urlopen)

    out = tmp_path / "outputs"
    out.mkdir()
    mission = _mission(sota_baseline_value=0.5, breakthrough_margin=0.01)
    (out / "metrics.json").write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 0.99,
                "baseline": 0.5,
                "coverage": 0.9,
                "math_checks": "PASS",
            }
        ),
        encoding="utf-8",
    )
    run_triage_for_mission(mission, out)
    assert len(posted) == 1
    assert posted[0]["tier"] == 3
    assert posted[0]["event"] == "paper_pipeline.triage.breakthrough"
    assert (out / "triage" / "events.jsonl").is_file()


def test_events_jsonl_without_webhook(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    (out / "metrics.json").write_text(
        json.dumps(
            {
                "exit_code": 0,
                "main": 0.81,
                "baseline": 0.8,
                "coverage": 0.9,
                "math_checks": "FAIL",
            }
        ),
        encoding="utf-8",
    )
    mission = _mission(sota_baseline_value=0.8, replication_tolerance=0.05)
    run_triage_for_mission(mission, out)
    lines = (out / "triage" / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["tier"] == 2


def test_lower_is_better_breakthrough() -> None:
    m = Mission(
        topic="t",
        paper_target="",
        quality_gates=QualityGatesConfig(
            sota_baseline_value=0.5,
            breakthrough_margin=0.1,
            higher_is_better=False,
        ),
    )
    r = classify_triage(
        TriageMetrics(exit_code=0, main=0.35, baseline=0.5, coverage=0.9, math_checks="PASS"),
        m,
    )
    assert r.tier == 3
