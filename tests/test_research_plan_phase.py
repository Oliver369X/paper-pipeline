"""Tests for research plan phase."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.research_plan_phase import _normalize_plan, run_research_plan_phase
from paper_pipeline.state import RunState


def test_normalize_plan_fills_sections() -> None:
    mission = Mission(
        topic="test topic",
        sections_needed=["related_work", "gaps"],
    )
    plan = _normalize_plan({"sections": {}}, mission)
    assert plan["schema_version"] == 1
    assert "related_work" in plan["sections"]
    assert len(plan["sections"]["related_work"]["queries"]) >= 1


def test_research_plan_writes_json(tmp_path: Path) -> None:
    mission = Mission(topic="AI agents", sections_needed=["gaps"], provider="mistral")
    state = RunState()
    state_path = tmp_path / "run_state.json"
    client = MagicMock()
    client.ask_single.return_value = json.dumps(
        {"sections": {"gaps": {"queries": ["What gaps exist in agent eval?"], "mode": "discovery"}}}
    )
    plog = MagicMock()
    calls, code = run_research_plan_phase(
        mission, client, state, state_path, tmp_path, plog, 0, manifest=None
    )
    assert code == 0
    assert calls == 1
    plan_path = tmp_path / "research_plan.json"
    assert plan_path.is_file()
    data = json.loads(plan_path.read_text(encoding="utf-8"))
    assert "gaps" in data["sections"]
