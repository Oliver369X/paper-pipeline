"""Tests for deterministic metrics validation."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.pipeline.experiment_metrics_validate import validate_metrics_deterministic


def test_validate_ok_exit_zero(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(
        json.dumps({"exit_code": 0, "metrics": {"loss": 0.5}}, ensure_ascii=False),
        encoding="utf-8",
    )
    ok, reasons = validate_metrics_deterministic(out, None)
    assert ok
    assert reasons == []


def test_validate_fail_exit_nonzero(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(
        json.dumps({"exit_code": 1}, ensure_ascii=False),
        encoding="utf-8",
    )
    ok, reasons = validate_metrics_deterministic(out, None)
    assert not ok
    assert any("exit_code" in r for r in reasons)


def test_validate_bounds(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(
        json.dumps({"exit_code": 0, "metrics": {"loss": 99.0}}, ensure_ascii=False),
        encoding="utf-8",
    )
    bounds = {"metrics.loss": {"min": 0, "max": 10}}
    ok, reasons = validate_metrics_deterministic(out, bounds)
    assert not ok
    assert any("above max" in r for r in reasons)


def test_validate_nan(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(
        json.dumps({"exit_code": 0, "x": float("nan")}, allow_nan=True),
        encoding="utf-8",
    )
    ok, reasons = validate_metrics_deterministic(out, None)
    assert not ok
    assert any("non-finite" in r for r in reasons)
