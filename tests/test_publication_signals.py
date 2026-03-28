"""Publish signals: tier × quality matrix."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.mission import Mission
from paper_pipeline.publication.publish_manager import write_publish_decision
from paper_pipeline.publication.signals import compute_publish_signals


def _mission() -> Mission:
    return Mission(
        topic="t",
        paper_target="p",
        sections_needed=["gaps"],
        output_dir="outputs",
        mission_version=1,
        enable_quality_check=True,
    )


def _write_qv(out: Path, publishable: bool) -> None:
    d = out / "validation"
    d.mkdir(parents=True, exist_ok=True)
    (d / "quality_validation.json").write_text(
        json.dumps(
            {
                "publishable": publishable,
                "blocking_reasons": [] if publishable else ["fail"],
            },
        ),
        encoding="utf-8",
    )


def _write_triage(out: Path, tier: int) -> None:
    t = out / "triage"
    t.mkdir(parents=True, exist_ok=True)
    (t / "triage_report.json").write_text(
        json.dumps({"tier": tier, "label": "x", "version": 1}),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("tier", "quality_ok", "eligible"),
    [
        (3, True, True),
        (3, False, False),
        (2, True, True),
        (0, True, True),
    ],
)
def test_tier_quality_matrix(
    tmp_path: Path,
    tier: int,
    quality_ok: bool,
    eligible: bool,
) -> None:
    out = tmp_path / "o"
    out.mkdir()
    _write_qv(out, quality_ok)
    _write_triage(out, tier)
    m = _mission()
    sig = compute_publish_signals(out, m)
    assert sig["eligible_for_publication"] is eligible
    if tier == 3 and not quality_ok:
        assert "tier3_without_quality_gates" in sig["blocking_reasons"]


def test_tier_three_blocked_without_quality_file(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    _write_triage(out, 3)
    m = _mission()
    sig = compute_publish_signals(out, m)
    assert sig["eligible_for_publication"] is False
    assert "tier3_without_quality_gates" in sig["blocking_reasons"]


def test_publish_decision_writes_safety_trace_for_breakthrough(tmp_path: Path) -> None:
    out = tmp_path / "o"
    out.mkdir()
    _write_qv(out, True)
    _write_triage(out, 3)
    m = _mission()

    write_publish_decision(out, m)

    trace = out / "safety_trace.jsonl"
    assert trace.is_file()
    rows = trace.read_text(encoding="utf-8").splitlines()
    assert rows
    payload = json.loads(rows[-1])
    assert payload["candidate_action"] == "publish_consolidation"
    assert payload["decision"] == "REQUIRE_HUMAN_APPROVAL"
    memory = out / "research_memory.jsonl"
    assert memory.is_file()
    mem_rows = memory.read_text(encoding="utf-8").splitlines()
    assert mem_rows
    mem_payload = json.loads(mem_rows[-1])
    assert mem_payload["kind"] == "publish"
