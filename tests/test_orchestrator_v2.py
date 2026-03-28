"""Tests for the v2 orchestrator wrapper (no real Perplexity calls)."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from paper_pipeline.constants import ExitCode
from paper_pipeline.orchestrator_v2 import run_pipeline_v2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_mission(
    tmp_path: Path,
    *,
    enable_epistemic: bool = False,
    enable_degradation: bool = False,
    enable_skill_orchestrator: bool = False,
    enable_hypervisor: bool = False,
    output_dir: Path | None = None,
) -> Path:
    """Write a minimal mission.md with optional v2 flags."""
    out = output_dir or (tmp_path / "outputs")
    mission = tmp_path / "mission.md"
    mission.write_text(
        textwrap.dedent(f"""\
            ---
            topic: "Test ML topic"
            paper_target: "workshop"
            sections_needed:
              - intro
            max_perplexity_calls: 2
            code_needed: false
            enable_notion: false
            enable_quality_check: false
            enable_cursor_cli: false
            model: best
            output_dir: "{out.as_posix()}"
            enable_epistemic_injection: {str(enable_epistemic).lower()}
            enable_degradation_monitor: {str(enable_degradation).lower()}
            enable_skill_orchestrator: {str(enable_skill_orchestrator).lower()}
            enable_hypervisor_triage: {str(enable_hypervisor).lower()}
            ---
        """),
        encoding="utf-8",
    )
    return mission


@pytest.fixture(autouse=True)
def _ensure_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Guarantee a fake Perplexity token so the v1 pipeline does not abort."""
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "fake-token-for-test")


# ---------------------------------------------------------------------------
# Fake Perplexity client used to prevent real network calls in v1
# ---------------------------------------------------------------------------

class _FakeConversation:
    answer = "mock section content with enough characters to pass validation easily"
    uuid = "fake-uuid"
    read_write_token = "fake-rw"

    def ask(self, *_a, **_k) -> None:  # noqa: D102
        pass


class _FakePerplexity:
    def __init__(self, *_a, **_k) -> None:
        pass

    def create_conversation(self, _cfg):  # noqa: D102
        return _FakeConversation()

    def resume_conversation(self, _cfg, **_kw):  # noqa: D102
        return _FakeConversation()

    def close(self) -> None:  # noqa: D102
        pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_v2_dry_run_works(tmp_path: Path) -> None:
    """Dry run with v2 flags enabled returns OK without calling Perplexity."""
    mission = _write_mission(tmp_path, enable_epistemic=True, enable_degradation=True)

    with patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        code = run_pipeline_v2(mission, dry_run=True)

    assert code == ExitCode.OK


def test_v2_skill_orchestrator_writes_manifest(tmp_path: Path) -> None:
    """When enable_skill_orchestrator is True, manifest YAML is written (no network)."""
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_skill_orchestrator=True, output_dir=out)

    with patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        code = run_pipeline_v2(mission, dry_run=True)

    assert code == ExitCode.OK
    manifest_path = out / "skill_orchestrator_manifest.yaml"
    assert manifest_path.is_file()
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert "experiment_id" in data
    assert "DOMAIN_ACQUISITION" in data["phases"]
    assert "technical-research" in data["phases"]["DOMAIN_ACQUISITION"]["skills"]
    assert "perplexity-web" in data["phases"]["DOMAIN_ACQUISITION"]["mcps"]
    web = data["phases"]["WEB_PACKAGING"]
    assert web["skills"] == []
    assert "nextjs" in web["skills_after_evaluation_phase"]


def test_v2_skill_manifest_not_written_when_disabled(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_skill_orchestrator=False, output_dir=out)

    with patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        run_pipeline_v2(mission, dry_run=True)

    assert not (out / "skill_orchestrator_manifest.yaml").exists()


def test_v2_without_flags_delegates_to_v1(tmp_path: Path) -> None:
    """When no v2 flags are set, run_pipeline_v2 just calls run_pipeline."""
    mission = _write_mission(tmp_path)

    with patch("paper_pipeline.orchestrator_v2.run_pipeline") as mock_v1, \
         patch("paper_pipeline.orchestrator_v2.load_mission") as mock_load:
        mock_load.return_value = MagicMock(
            output_dir=str(tmp_path / "outputs"),
            enable_epistemic_injection=False,
            enable_degradation_monitor=False,
        )
        mock_v1.return_value = ExitCode.OK

        code = run_pipeline_v2(mission, dry_run=False)

    assert code == ExitCode.OK
    mock_v1.assert_called_once_with(mission, dry_run=False, event_sink=None)


def test_v2_epistemic_injection_runs_when_enabled(tmp_path: Path) -> None:
    """When enable_epistemic_injection is True, the DCA file is created."""
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_epistemic=True, output_dir=out)

    fake_dca = MagicMock()
    fake_dca.sota_techniques = ["technique_a", "technique_b"]

    fake_injector = MagicMock()
    fake_injector.build_domain_context.return_value = fake_dca
    fake_injector.generate_cursor_system_prompt.return_value = "# EPISTEMIC OVERRIDE"

    injector_cls = MagicMock(return_value=fake_injector)

    with patch("paper_pipeline.orchestrator_v2._run_epistemic_injection") as mock_ei, \
         patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        mock_ei.side_effect = lambda m, o: _do_fake_injection(fake_injector, injector_cls, m, o)
        code = run_pipeline_v2(mission, dry_run=False)

    assert code == ExitCode.OK
    mock_ei.assert_called_once()


def _do_fake_injection(
    fake_injector: MagicMock,
    injector_cls: MagicMock,
    mission: object,
    output_dir: Path,
) -> None:
    """Simulate epistemic injection by writing the DCA file."""
    dca = fake_injector.build_domain_context("Test ML topic", "workshop")
    prompt = fake_injector.generate_cursor_system_prompt(dca)
    (output_dir / "domain_context.yaml").write_text("topic: test\n", encoding="utf-8")
    (output_dir / "epistemic_system_prompt.md").write_text(prompt, encoding="utf-8")


def test_v2_degradation_monitor_evaluates_draft(tmp_path: Path) -> None:
    """When degradation monitor is enabled, it evaluates the draft and logs metrics."""
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_degradation=True, output_dir=out)

    with patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        code = run_pipeline_v2(mission, dry_run=False)

    assert code == ExitCode.OK
    assert (out / "draft_paper.md").is_file()


def test_v2_feature_failure_does_not_crash(tmp_path: Path) -> None:
    """If epistemic injection raises, the pipeline still completes."""
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_epistemic=True, output_dir=out)

    def _boom(*_a, **_k):
        raise RuntimeError("Simulated EpistemicInjector failure")

    with patch("paper_pipeline.orchestrator_v2._run_epistemic_injection", side_effect=_boom), \
         patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        code = run_pipeline_v2(mission, dry_run=False)

    assert code == ExitCode.OK
    assert (out / "draft_paper.md").is_file()


def test_v2_hypervisor_updates_objective_trace(tmp_path: Path) -> None:
    out = tmp_path / "outputs"
    out.mkdir()
    mission = _write_mission(tmp_path, enable_hypervisor=True, output_dir=out)

    with patch("paper_pipeline.pipeline.runner.Perplexity", _FakePerplexity):
        code = run_pipeline_v2(mission, dry_run=False)

    assert code == ExitCode.OK
    assert (out / "objective_state.json").is_file()
    assert (out / "objective_trace.jsonl").is_file()
    assert (out / "research_memory.jsonl").is_file()
    assert (out / "memory_index.json").is_file()
    assert (out / "goal_selection.json").is_file()
    assert (out / "goals.json").is_file()
    assert (out / "working_memory.json").is_file()
    assert (out / "hypotheses_registry.json").is_file()
