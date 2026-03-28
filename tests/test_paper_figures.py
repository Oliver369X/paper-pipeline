"""Tests for reporting figures (matplotlib optional for PNG)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.reporting.paper_figures import (
    load_metrics_dict,
    sota_claim_paragraph_en,
)


def test_load_metrics_dict(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps({"main": 0.91, "baseline": 0.88}), encoding="utf-8")
    d = load_metrics_dict(p)
    assert d["main"] == 0.91
    assert d["baseline"] == 0.88


def test_sota_claim_paragraph_en() -> None:
    text = sota_claim_paragraph_en(
        metric_name="accuracy",
        measured=0.91,
        baseline=0.88,
        beats_baseline=True,
        tolerance=0.01,
    )
    assert "0.9100" in text or "0.91" in text
    assert "baseline" in text.lower()


def test_figure_main_vs_baseline_writes_png(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    from paper_pipeline.reporting.paper_figures import figure_main_vs_baseline

    m = tmp_path / "metrics.json"
    m.write_text(json.dumps({"main": 0.92, "baseline": 0.85}), encoding="utf-8")
    out = tmp_path / "fig.png"
    figure_main_vs_baseline(m, out, language="en")
    assert out.is_file()
    assert out.stat().st_size > 100
