"""paper-loop stall: loop_state + stop_decision (no network)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from paper_pipeline.constants import ExitCode


def test_loop_stall_writes_stop_decision(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir(parents=True)
    mpath = tmp_path / "mission.md"
    mpath.write_text(
        "---\n"
        "topic: t\n"
        "paper_target: p\n"
        f"output_dir: {out.as_posix()}\n"
        "sections_needed: [gaps]\n"
        "---\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("LOOP_STALL_DETECT", "1")
    monkeypatch.setenv("LOOP_STALL_MAX_CONSECUTIVE", "2")
    monkeypatch.setenv("LOOP_MIN_DELTA_CHARS", "20")

    def _fake_run(*_a: object, **_k: object) -> int:
        (out / "draft_paper.md").write_text("identical draft\n", encoding="utf-8")
        return 0

    monkeypatch.setattr(
        "paper_pipeline.integrated_loop_main.run_integrated_cycle",
        _fake_run,
    )
    monkeypatch.setattr(sys, "argv", ["x", str(mpath), "--max-cycles", "4", "--no-meta"])

    from paper_pipeline.integrated_loop_main import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == ExitCode.LOOP_STALLED
    stop_p = out / "loop" / "stop_decision.json"
    assert stop_p.is_file()
    data = json.loads(stop_p.read_text(encoding="utf-8"))
    assert data["status"] == "stopped"
    assert (out / "loop" / "loop_state.json").is_file()
    trace_p = out / "safety_trace.jsonl"
    assert trace_p.is_file()
    rows = trace_p.read_text(encoding="utf-8").splitlines()
    assert rows
    payload = json.loads(rows[-1])
    assert payload["candidate_action"] == "loop_iteration"
    assert payload["decision"] == "BLOCK"
    objective_state = out / "objective_state.json"
    assert objective_state.is_file()
    obj = json.loads(objective_state.read_text(encoding="utf-8"))
    assert obj["gates"]["loop_stopped"] is True
    objective_trace = out / "objective_trace.jsonl"
    assert objective_trace.is_file()
    memory = out / "research_memory.jsonl"
    assert memory.is_file()
    mem_rows = memory.read_text(encoding="utf-8").splitlines()
    assert mem_rows
    mem_payload = json.loads(mem_rows[-1])
    assert mem_payload["kind"] == "loop_stop"
    goal_selection = out / "goal_selection.json"
    assert goal_selection.is_file()
    gs = json.loads(goal_selection.read_text(encoding="utf-8"))
    assert gs["selected_goal_type"] == "wait_human"
    assert (out / "goals.json").is_file()
    assert (out / "working_memory.json").is_file()
    assert (out / "hypotheses_registry.json").is_file()
