"""Tests del orquestador con Perplexity simulado (sin red)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from paper_pipeline.orchestrator import run_pipeline


@pytest.fixture
def fake_perplexity():
    """Reemplaza el cliente Perplexity por uno que solo cuenta llamadas."""

    calls: list[str] = []

    class FakeConversation:
        answer = "respuesta_mock"
        uuid = "fake-backend-uuid"
        read_write_token = "fake-rw-token"

        def ask(self, *_args, **_kwargs) -> None:
            calls.append("ask")

    class FakePerplexity:
        def __init__(self, *_a, **_k) -> None:
            pass

        def create_conversation(self, _cfg) -> FakeConversation:
            calls.append("create_conversation")
            return FakeConversation()

        def resume_conversation(self, _cfg, *, backend_uuid: str, read_write_token: str | None = None) -> FakeConversation:
            calls.append(f"resume:{backend_uuid[:4]}")
            return FakeConversation()

        def close(self) -> None:
            pass

    with patch("paper_pipeline.pipeline.runner.Perplexity", FakePerplexity):
        yield calls


def test_pipeline_writes_section_files(tmp_path: Path, fake_perplexity: list[str]) -> None:
    out_abs = (tmp_path / "out_test").resolve()
    mission = tmp_path / "mission.md"
    mission.write_text(
        f"""---
topic: "Test topic ML"
paper_target: "workshop"
sections_needed: [gaps, sota]
max_perplexity_calls: 10
code_needed: false
enable_notion: false
enable_quality_check: false
model: best
output_dir: "{out_abs.as_posix()}"
---
""",
        encoding="utf-8",
    )
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "fake-token-for-test"

    code = run_pipeline(mission, dry_run=False)
    assert code == 0

    out = out_abs
    assert (out / "gaps.md").is_file()
    assert (out / "sota.md").is_file()
    assert (out / "draft_paper.md").is_file()
    assert (out / "objective_state.json").is_file()
    assert (out / "objective_trace.jsonl").is_file()
    assert (out / "research_memory.jsonl").is_file()
    assert (out / "memory_index.json").is_file()
    assert (out / "goal_selection.json").is_file()
    assert (out / "goals.json").is_file()
    assert (out / "working_memory.json").is_file()
    assert (out / "hypotheses_registry.json").is_file()
    assert "gaps" in (out / "gaps.md").read_text(encoding="utf-8")
    assert fake_perplexity.count("create_conversation") == 2
    assert fake_perplexity.count("ask") == 2


def test_pipeline_single_thread_one_conversation(tmp_path: Path, fake_perplexity: list[str]) -> None:
    out_abs = (tmp_path / "out_single").resolve()
    mission = tmp_path / "mission.md"
    mission.write_text(
        f"""---
topic: "Test topic ML"
paper_target: "workshop"
sections_needed: [gaps, sota]
max_perplexity_calls: 10
code_needed: false
enable_notion: false
enable_quality_check: false
single_thread_perplexity: true
model: best
output_dir: "{out_abs.as_posix()}"
---
""",
        encoding="utf-8",
    )
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "fake-token-for-test"

    code = run_pipeline(mission, dry_run=False)
    assert code == 0
    assert fake_perplexity.count("create_conversation") == 1
    assert fake_perplexity.count("ask") == 2


def test_pipeline_stops_at_max_perplexity_calls(tmp_path: Path, fake_perplexity: list[str]) -> None:
    out_abs = (tmp_path / "out_max").resolve()
    mission = tmp_path / "mission.md"
    mission.write_text(
        f"""---
topic: "T"
paper_target: "P"
sections_needed: [related_work, sota, gaps, methodology]
max_perplexity_calls: 2
code_needed: false
enable_notion: false
enable_quality_check: false
model: best
output_dir: "{out_abs.as_posix()}"
---
""",
        encoding="utf-8",
    )
    os.environ["PERPLEXITY_SESSION_TOKEN"] = "fake-token-for-test"

    code = run_pipeline(mission, dry_run=False)
    assert code == 0

    out = out_abs
    assert (out / "related_work.md").is_file()
    assert (out / "sota.md").is_file()
    assert not (out / "gaps.md").is_file()
    assert fake_perplexity.count("ask") == 2


def test_dry_run_no_perplexity_calls(tmp_path: Path) -> None:
    mission = tmp_path / "m.md"
    mission.write_text(
        "---\ntopic: X\npaper_target: Y\nsections_needed: [gaps]\nmax_perplexity_calls: 3\n---\n",
        encoding="utf-8",
    )
    with patch("paper_pipeline.pipeline.runner.Perplexity") as m:
        code = run_pipeline(mission, dry_run=True)
        m.assert_not_called()
    assert code == 0
