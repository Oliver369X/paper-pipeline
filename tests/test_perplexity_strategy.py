"""Perplexity Strategy V1: pure helpers + optional JSONL (no live API)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.agent.perplexity_strategy import (
    RECORD_NAME,
    CallRecord,
    append_call_record,
    perplexity_strategy_enabled,
    query_fingerprint,
    record_planned_call,
    resolve_profile_for_section,
)


def test_query_fingerprint_stable() -> None:
    a = query_fingerprint("hello  world", "sec1")
    b = query_fingerprint("hello world", "sec1")
    assert a == b
    assert len(a) == 24


def test_resolve_profile_related_work_is_discovery() -> None:
    plan = resolve_profile_for_section("related_work", "best")
    assert plan.mode == "discovery"
    assert plan.profile_id == "deep_discovery"
    assert plan.cost_class == "high"


def test_resolve_profile_methodology_is_verification() -> None:
    plan = resolve_profile_for_section("methodology", "sonar")
    assert plan.mode == "verification"
    assert plan.model == "sonar"


def test_perplexity_strategy_disabled_by_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("PAPER_PIPELINE_PERPLEXITY_STRATEGY", raising=False)
    assert perplexity_strategy_enabled() is False
    p = record_planned_call(
        tmp_path,
        prompt="q",
        section="gaps",
        mission_model="m",
    )
    assert p is None
    assert not (tmp_path / RECORD_NAME).exists()


def test_record_planned_call_writes_jsonl(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_PERPLEXITY_STRATEGY", "1")
    assert perplexity_strategy_enabled() is True
    path = record_planned_call(
        tmp_path,
        prompt="What are the gaps?",
        section="gaps",
        mission_model="best",
        mission_id="mid",
    )
    assert path is not None
    assert path.is_file()
    line = path.read_text(encoding="utf-8").strip()
    row = json.loads(line)
    assert row["section_or_goal"] == "gaps"
    assert row["model"] == "best"
    assert row["mission_id"] == "mid"
    assert "query_hash" in row


def test_append_call_record_idempotent_lines(tmp_path: Path) -> None:
    rec = CallRecord(
        ts="t",
        query_hash="h",
        profile_id="p",
        mode="synthesis",
        model="m",
        cost_class="low",
        section_or_goal="s",
    )
    append_call_record(tmp_path, rec)
    append_call_record(tmp_path, rec)
    lines = (tmp_path / RECORD_NAME).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
