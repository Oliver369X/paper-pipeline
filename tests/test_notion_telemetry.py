"""Notion triage telemetry (mocked HTTP via append_section_to_page)."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_pipeline.mission import Mission
from paper_pipeline.notion_telemetry import maybe_append_triage_breakthrough_to_notion


def test_notion_skipped_without_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, str, str]] = []

    def fake_append(token: str, page_id: str, section_title: str, markdown_body: str) -> None:
        calls.append((token, page_id, section_title, markdown_body))

    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv("NOTION_TRIAGE_PAGE_ID", raising=False)
    monkeypatch.setattr(
        "paper_pipeline.notion_telemetry.append_section_to_page",
        fake_append,
    )
    maybe_append_triage_breakthrough_to_notion(
        Mission(topic="x", paper_target="y"),
        tier=3,
        label="breakthrough",
        reason="r",
        detail={},
        metrics={},
        output_dir=tmp_path,
    )
    assert calls == []


def test_notion_called_tier3_with_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, str, str]] = []

    def fake_append(token: str, page_id: str, section_title: str, markdown_body: str) -> None:
        calls.append((token, page_id, section_title, markdown_body))

    monkeypatch.setenv("NOTION_TOKEN", "test-token")
    monkeypatch.setenv("NOTION_TRIAGE_PAGE_ID", "page-uuid-1")
    monkeypatch.setattr(
        "paper_pipeline.notion_telemetry.append_section_to_page",
        fake_append,
    )

    maybe_append_triage_breakthrough_to_notion(
        Mission(topic="Topic X", paper_target="venue"),
        tier=3,
        label="breakthrough",
        reason="metric",
        detail={"k": 1},
        metrics={"main": 0.99},
        output_dir=tmp_path,
    )
    assert len(calls) == 1
    token, page_id, title, body = calls[0]
    assert token == "test-token"
    assert page_id == "page-uuid-1"
    assert "Breakthrough" in title
    assert "Topic X" in body
    assert "venue" in body


def test_notion_not_called_tier2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_append(*a: object, **k: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setenv("NOTION_TOKEN", "t")
    monkeypatch.setenv("NOTION_TRIAGE_PAGE_ID", "p")
    monkeypatch.setattr(
        "paper_pipeline.notion_telemetry.append_section_to_page",
        fake_append,
    )
    maybe_append_triage_breakthrough_to_notion(
        Mission(topic="x", paper_target="y"),
        tier=2,
        label="match",
        reason="r",
        detail={},
        metrics={},
        output_dir=tmp_path,
    )
    assert called is False
