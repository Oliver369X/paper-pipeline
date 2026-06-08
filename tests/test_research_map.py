"""Tests for research map."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.research_map import write_research_map


def test_research_map_after_draft(tmp_path: Path) -> None:
    mission = Mission(topic="t", sections_needed=["gaps"])
    (tmp_path / "gaps.md").write_text("content", encoding="utf-8")
    (tmp_path / "draft_paper.md").write_text("# draft", encoding="utf-8")
    p = write_research_map(tmp_path, mission)
    assert p.is_file()
    import json

    data = json.loads(p.read_text(encoding="utf-8"))
    statuses = {n["id"]: n["status"] for n in data["nodes"]}
    assert statuses["literature"] == "done"
    assert statuses["writing"] == "done"
