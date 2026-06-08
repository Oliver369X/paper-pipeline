"""Tests for research agent trace."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from paper_pipeline.mission import Mission, ResearchAgentConfig
from paper_pipeline.pipeline.research_agent_phase import run_research_agent_phase


def test_research_agent_disabled() -> None:
    mission = Mission(topic="t", research_agent=ResearchAgentConfig(enabled=False))
    client = MagicMock()
    assert run_research_agent_phase(mission, client, Path("outputs"), MagicMock(), manifest=None) == 0
    client.ask_single.assert_not_called()


def test_research_agent_writes_trace(tmp_path: Path) -> None:
    mission = Mission(
        topic="agents",
        sections_needed=["gaps", "sota"],
        research_agent=ResearchAgentConfig(enabled=True, max_concurrent=2),
    )
    client = MagicMock()
    client.ask_single.return_value = '{"subtasks": []}'
    code = run_research_agent_phase(mission, client, tmp_path, MagicMock(), manifest=None)
    assert code == 0
    trace = tmp_path / "research_agent_trace.jsonl"
    assert trace.is_file()
    lines = trace.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 3
