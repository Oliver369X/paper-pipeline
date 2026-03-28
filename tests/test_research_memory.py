"""ResearchMemory V1 contract and persistence tests."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.agent.research_memory import (
    append_research_memory,
    compact_memory_dry_run,
    format_recent_memory_for_brain_prompt,
    load_memory_index,
    query_memory_entries_for_goal,
    rebuild_memory_index,
)


def test_append_research_memory_writes_jsonl(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)

    path = append_research_memory(
        out,
        kind="publish",
        summary="Publicación elegible con tier 2",
        source_artifacts=["publication/publish_decision.json", "triage/triage_report.json"],
        payload={"eligible_for_publication": True, "triage_tier": 2},
        tags=["publish", "tier2"],
        confidence=0.8,
        mission_id="m1",
        run_id="r1",
    )

    assert path.is_file()
    rows = path.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1
    entry = json.loads(rows[0])
    assert entry["kind"] == "publish"
    assert entry["summary"] == "Publicación elegible con tier 2"
    assert entry["mission_id"] == "m1"
    assert entry["run_id"] == "r1"


def test_rebuild_memory_index_counts_by_kind(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)

    append_research_memory(
        out,
        kind="quality",
        summary="Quality gates OK",
        source_artifacts=["validation/quality_validation.json"],
        payload={"publishable": True},
    )
    append_research_memory(
        out,
        kind="publish",
        summary="Publish bloqueado por quality gates",
        source_artifacts=["publication/publish_decision.json"],
        payload={"eligible_for_publication": False},
    )
    append_research_memory(
        out,
        kind="publish",
        summary="Publish elegible",
        source_artifacts=["publication/publish_decision.json"],
        payload={"eligible_for_publication": True},
    )

    index_path = rebuild_memory_index(out)
    index = load_memory_index(index_path)

    assert index_path.is_file()
    assert index["counts_by_kind"]["quality"] == 1
    assert index["counts_by_kind"]["publish"] == 2
    assert index["latest_by_kind"]["publish"]["summary"] == "Publish elegible"


def test_rebuild_memory_index_tracks_last_event(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)

    append_research_memory(
        out,
        kind="loop_stop",
        summary="Loop detenido por stall",
        source_artifacts=["loop/stop_decision.json"],
        payload={"status": "stopped"},
    )

    index = load_memory_index(rebuild_memory_index(out))

    assert index["last_event"]["kind"] == "loop_stop"
    assert "source_artifacts" in index["last_event"]


def test_query_memory_entries_for_goal_by_tag(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    append_research_memory(
        out,
        kind="triage",
        summary="A",
        source_artifacts=[],
        payload={},
        tags=["literature"],
    )
    append_research_memory(
        out,
        kind="publish",
        summary="B",
        source_artifacts=[],
        payload={},
        tags=["other"],
    )
    rows = query_memory_entries_for_goal(out, "literature", limit=10)
    assert len(rows) == 1
    assert rows[0]["summary"] == "A"


def test_query_memory_entries_for_goal_by_payload_goal_type(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    append_research_memory(
        out,
        kind="quality",
        summary="C",
        source_artifacts=[],
        payload={"goal_type": "verification"},
    )
    rows = query_memory_entries_for_goal(out, "verification", limit=5)
    assert len(rows) == 1
    assert rows[0]["summary"] == "C"


def test_compact_memory_dry_run(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    rep = compact_memory_dry_run(out)
    assert rep["dry_run"] is True
    assert rep["entries_total"] == 0


def test_format_recent_memory_for_brain_prompt(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    append_research_memory(
        out,
        kind="brain_brief",
        summary="Resumen breve de brief",
        source_artifacts=["outputs/brain_brief.md"],
        payload={"mission_id": "mid1"},
        tags=["brain", "brief"],
        mission_id="mid1",
    )
    text = format_recent_memory_for_brain_prompt(out, max_chars=4000)
    assert "brain_brief" in text
    assert "Resumen breve" in text


def test_format_recent_memory_for_brain_prompt_empty(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    assert format_recent_memory_for_brain_prompt(out, max_chars=100) == ""

