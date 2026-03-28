"""Pipeline honesty: métricas, invalidación de resume, artefactos de réplica."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_pipeline.pipeline.experiment_phase import ExperimentRunnerResult, read_metrics_exit_code
from paper_pipeline.pipeline.replication_status import write_replication_artifacts
from paper_pipeline.pipeline.run_state_policy import invalidate_resume_after_critical_failure
from paper_pipeline.state import RunState


def test_read_metrics_exit_code(tmp_path: Path) -> None:
    (tmp_path / "metrics.json").write_text('{"exit_code": 1, "main": null}', encoding="utf-8")
    assert read_metrics_exit_code(tmp_path) == 1
    assert read_metrics_exit_code(tmp_path / "missing") is None


def test_invalidate_resume_strips_quality_check_only(tmp_path: Path) -> None:
    sp = tmp_path / "run_state.json"
    st = RunState()
    st.completed_steps = ["perplexity:gaps", "step:quality_check"]
    st.save(sp)
    st2 = RunState.load(sp)
    invalidate_resume_after_critical_failure(st2, sp, cause="experiment_runner")
    st3 = RunState.load(sp)
    assert "step:quality_check" not in st3.completed_steps
    assert "perplexity:gaps" in st3.completed_steps
    assert st3.last_critical_failure == "experiment_runner"


def test_invalidate_resume_strips_perplexity_when_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_INVALIDATE_PERPLEXITY_ON_EXP_FAIL", "1")
    sp = tmp_path / "run_state.json"
    st = RunState()
    st.completed_steps = ["perplexity:gaps", "step:quality_check"]
    st.save(sp)
    st2 = RunState.load(sp)
    invalidate_resume_after_critical_failure(st2, sp, cause="experiment")
    st3 = RunState.load(sp)
    assert not any(x.startswith("perplexity:") for x in st3.completed_steps)


def test_write_replication_artifacts_prepends_draft(tmp_path: Path) -> None:
    draft = tmp_path / "draft_paper.md"
    draft.write_text("# Draft\n", encoding="utf-8")
    write_replication_artifacts(
        tmp_path,
        draft,
        ExperimentRunnerResult(ok=False, exit_code=1, reason="unit test", replication_tier="failed"),
        mission_topic="topic",
    )
    assert (tmp_path / "replication_status.md").is_file()
    assert (tmp_path / "experiment_diagnostics.json").is_file()
    body = draft.read_text(encoding="utf-8")
    assert "Replication status: FAILED" in body
    assert "unit test" in body
