"""Smoke tests for preprint figure helpers (requires matplotlib)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
from paper_pipeline.agent_eval.eval_runner import run_all


pytest.importorskip("matplotlib")

from paper_pipeline.reporting.preprint_figures import (  # noqa: E402
    figure_agent_eval_per_scenario,
    figure_scorecard_radar,
)


def test_figure_agent_eval_per_scenario_writes_png(tmp_path: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td))
    payload = scorecard_to_stable_dict(report)
    out = tmp_path / "x.png"
    figure_agent_eval_per_scenario(out, payload)
    assert out.is_file()
    assert out.stat().st_size > 200


def test_figure_scorecard_radar_writes_png(tmp_path: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td))
    payload = scorecard_to_stable_dict(report)
    out = tmp_path / "r.png"
    figure_scorecard_radar(out, payload)
    assert out.is_file()


def test_figure_claims_rich_requires_list_json(tmp_path: Path) -> None:
    from paper_pipeline.reporting.preprint_figures import figure_claims_rich

    p = tmp_path / "claims.json"
    p.write_text(json.dumps([{"type": "a"}, {"type": "b"}, {"type": "a"}]), encoding="utf-8")
    out = tmp_path / "c.png"
    figure_claims_rich(out, p)
    assert out.is_file()
