"""Tests for v2 Mission fields — backward compatibility and new nested configs."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.mission import (
    ComputeConfig,
    DebuggingConfig,
    EpistemicInjectionConfig,
    Hypothesis,
    Mission,
    QualityGatesConfig,
    SafetyConfig,
    load_mission,
    save_mission,
)

RACING_MISSION = Path(__file__).resolve().parent.parent / "missions" / "racing_game_3d" / "mission.md"


def test_v1_mission_still_loads() -> None:
    """The existing racing_game_3d mission.md must load without errors."""
    m = load_mission(RACING_MISSION)
    assert m.topic.startswith("Juego web")
    assert m.code_needed is True
    assert m.language == "es-ES"
    # v2 fields should all be at their defaults
    assert m.hypotheses == []
    assert m.epistemic_injection.enabled is False
    assert m.compute.local_gpu_available is False
    assert m.quality_gates.target_metric == ""
    assert m.debugging.cursor_max_attempts == 3
    assert m.safety.max_cost_usd == 5.0
    assert m.enable_epistemic_injection is False
    assert m.enable_degradation_monitor is False
    assert m.enable_skill_orchestrator is False
    assert m.enable_hypervisor_triage is False


def test_v2_mission_with_all_fields(tmp_path: Path) -> None:
    """A mission.md that uses every v2 field must parse correctly."""
    p = tmp_path / "mission.md"
    p.write_text(
        """\
---
topic: "Full v2 mission"
paper_target: "NeurIPS 2026"
max_perplexity_calls: 16
code_needed: true
model: "sonar-pro"
language: "en-US"
output_dir: "outputs/v2"

hypotheses:
  - id: H1
    description: "Transformers beat CNNs on small data"
    priority: HIGH
    expected_outcome: "+5% accuracy"
  - id: H2
    description: "Data augmentation helps"

epistemic_injection:
  enabled: true
  n_papers_to_fetch: 50
  n_repos_to_fetch: 10
  poison_pills:
    - claim: "LLMs cannot reason"
      source: "arxiv:2401.99999"

compute:
  local_gpu_available: true
  local_gpu_memory_gb: 24.0
  colab_mcp_enabled: true
  delegate_threshold_gb: 8.0

quality_gates:
  target_metric: "accuracy"
  higher_is_better: true
  sota_baseline_value: 0.91
  breakthrough_margin: 0.03
  replication_tolerance: 0.005
  require_statistical_significance: true

debugging:
  cursor_max_attempts: 5
  perplexity_max_attempts: 4
  generate_human_briefing: false

safety:
  max_total_runtime_minutes: 60
  max_cost_usd: 2.5
  require_human_approval_before_publish: false
  allow_force_push: true

enable_epistemic_injection: true
enable_degradation_monitor: true
enable_skill_orchestrator: true
---
""",
        encoding="utf-8",
    )
    m = load_mission(p)

    assert m.topic == "Full v2 mission"
    assert m.paper_target == "NeurIPS 2026"
    assert m.max_perplexity_calls == 16

    assert len(m.hypotheses) == 2
    assert m.hypotheses[0].id == "H1"
    assert m.hypotheses[0].priority == "HIGH"
    assert m.hypotheses[1].expected_outcome == ""

    assert m.epistemic_injection.enabled is True
    assert m.epistemic_injection.n_papers_to_fetch == 50
    assert len(m.epistemic_injection.poison_pills) == 1

    assert m.compute.local_gpu_available is True
    assert m.compute.local_gpu_memory_gb == 24.0
    assert m.compute.delegate_threshold_gb == 8.0

    assert m.quality_gates.target_metric == "accuracy"
    assert m.quality_gates.sota_baseline_value == 0.91
    assert m.quality_gates.breakthrough_margin == 0.03

    assert m.debugging.cursor_max_attempts == 5
    assert m.debugging.generate_human_briefing is False

    assert m.safety.max_total_runtime_minutes == 60
    assert m.safety.allow_force_push is True

    assert m.enable_epistemic_injection is True
    assert m.enable_degradation_monitor is True
    assert m.enable_skill_orchestrator is True


def test_v2_defaults_when_absent() -> None:
    """A minimal mission (topic only) must have correct defaults for all v2 fields."""
    m = Mission(topic="Minimal")

    assert m.paper_target == "generic venue"
    assert "related_work" in m.sections_needed

    assert m.hypotheses == []

    assert isinstance(m.epistemic_injection, EpistemicInjectionConfig)
    assert m.epistemic_injection.enabled is False
    assert m.epistemic_injection.n_papers_to_fetch == 20
    assert m.epistemic_injection.n_repos_to_fetch == 5
    assert m.epistemic_injection.poison_pills == []

    assert isinstance(m.compute, ComputeConfig)
    assert m.compute.local_gpu_available is False
    assert m.compute.local_gpu_memory_gb == 0
    assert m.compute.colab_mcp_enabled is False
    assert m.compute.delegate_threshold_gb == 12.0

    assert isinstance(m.quality_gates, QualityGatesConfig)
    assert m.quality_gates.target_metric == ""
    assert m.quality_gates.higher_is_better is True
    assert m.quality_gates.sota_baseline_value == 0.0
    assert m.quality_gates.breakthrough_margin == 0.02
    assert m.quality_gates.replication_tolerance == 0.01
    assert m.quality_gates.require_statistical_significance is True

    assert isinstance(m.debugging, DebuggingConfig)
    assert m.debugging.cursor_max_attempts == 3
    assert m.debugging.perplexity_max_attempts == 2
    assert m.debugging.generate_human_briefing is True

    assert isinstance(m.safety, SafetyConfig)
    assert m.safety.max_total_runtime_minutes == 120
    assert m.safety.max_cost_usd == 5.0
    assert m.safety.require_human_approval_before_publish is True
    assert m.safety.allow_force_push is False

    assert m.enable_epistemic_injection is False
    assert m.enable_degradation_monitor is False
    assert m.enable_skill_orchestrator is False


def test_hypotheses_parsed(tmp_path: Path) -> None:
    """Three hypotheses in YAML must parse into a typed list."""
    p = tmp_path / "mission.md"
    p.write_text(
        """\
---
topic: "Hypothesis test"
hypotheses:
  - id: H1
    description: "First hypothesis"
    priority: HIGH
    expected_outcome: "Significant improvement"
  - id: H2
    description: "Second hypothesis"
    priority: LOW
  - id: H3
    description: "Third hypothesis"
---
""",
        encoding="utf-8",
    )
    m = load_mission(p)

    assert len(m.hypotheses) == 3
    assert all(isinstance(h, Hypothesis) for h in m.hypotheses)

    assert m.hypotheses[0].id == "H1"
    assert m.hypotheses[0].priority == "HIGH"
    assert m.hypotheses[0].expected_outcome == "Significant improvement"

    assert m.hypotheses[1].id == "H2"
    assert m.hypotheses[1].priority == "LOW"
    assert m.hypotheses[1].expected_outcome == ""

    assert m.hypotheses[2].id == "H3"
    assert m.hypotheses[2].priority == "MEDIUM"


def test_save_and_reload_v2(tmp_path: Path) -> None:
    """A v2 mission must survive a save/load round-trip with all fields intact."""
    original = Mission(
        topic="Round-trip test",
        paper_target="ICML 2026",
        code_needed=True,
        hypotheses=[
            Hypothesis(id="H1", description="Test hyp", priority="HIGH", expected_outcome="Better"),
            Hypothesis(id="H2", description="Another hyp"),
        ],
        epistemic_injection=EpistemicInjectionConfig(
            enabled=True,
            n_papers_to_fetch=30,
            n_repos_to_fetch=8,
            poison_pills=[{"claim": "test", "source": "test"}],
        ),
        compute=ComputeConfig(
            local_gpu_available=True,
            local_gpu_memory_gb=16.0,
            colab_mcp_enabled=True,
            delegate_threshold_gb=10.0,
        ),
        quality_gates=QualityGatesConfig(
            target_metric="f1",
            higher_is_better=True,
            sota_baseline_value=0.85,
            breakthrough_margin=0.05,
            replication_tolerance=0.02,
            require_statistical_significance=False,
        ),
        debugging=DebuggingConfig(
            cursor_max_attempts=10,
            perplexity_max_attempts=5,
            generate_human_briefing=False,
        ),
        safety=SafetyConfig(
            max_total_runtime_minutes=30,
            max_cost_usd=1.0,
            require_human_approval_before_publish=False,
            allow_force_push=True,
        ),
        enable_epistemic_injection=True,
        enable_degradation_monitor=True,
        enable_skill_orchestrator=True,
    )

    p = tmp_path / "mission.md"
    save_mission(original, p)
    reloaded = load_mission(p)

    assert reloaded.topic == original.topic
    assert reloaded.paper_target == original.paper_target
    assert reloaded.code_needed is True

    assert len(reloaded.hypotheses) == 2
    assert reloaded.hypotheses[0].id == "H1"
    assert reloaded.hypotheses[0].priority == "HIGH"
    assert reloaded.hypotheses[1].expected_outcome == ""

    assert reloaded.epistemic_injection.enabled is True
    assert reloaded.epistemic_injection.n_papers_to_fetch == 30
    assert len(reloaded.epistemic_injection.poison_pills) == 1

    assert reloaded.compute.local_gpu_memory_gb == 16.0
    assert reloaded.compute.colab_mcp_enabled is True

    assert reloaded.quality_gates.target_metric == "f1"
    assert reloaded.quality_gates.breakthrough_margin == 0.05
    assert reloaded.quality_gates.require_statistical_significance is False

    assert reloaded.debugging.cursor_max_attempts == 10
    assert reloaded.debugging.generate_human_briefing is False

    assert reloaded.safety.max_total_runtime_minutes == 30
    assert reloaded.safety.allow_force_push is True

    assert reloaded.enable_epistemic_injection is True
    assert reloaded.enable_degradation_monitor is True
    assert reloaded.enable_skill_orchestrator is True
