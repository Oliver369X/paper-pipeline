"""Parse mission.md (YAML frontmatter + optional body).

Supports both v1 (flat fields) and v2 (nested config blocks) mission files.
All v2 fields are optional with sensible defaults so v1 missions load unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# v2 nested configuration models
# ---------------------------------------------------------------------------


class Hypothesis(BaseModel):
    """A single research hypothesis to validate during the pipeline run."""

    id: str
    description: str
    priority: str = "MEDIUM"
    expected_outcome: str = ""


def normalize_hypothesis_dict_list(items: list[Any]) -> list[dict[str, Any]]:
    """Coerce LLM/API shapes (p. ej. ``statement`` en vez de ``description``) a dicts compatibles con :class:`Hypothesis`."""

    out: list[dict[str, Any]] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        d = dict(item)
        desc = d.get("description") if isinstance(d.get("description"), str) else None
        if not (desc and str(desc).strip()):
            for alt in ("statement", "text", "content", "hypothesis"):
                v = d.get(alt)
                if isinstance(v, str) and v.strip():
                    d["description"] = v.strip()
                    break
        if not isinstance(d.get("description"), str) or not d["description"].strip():
            continue
        hid = d.get("id")
        if not (isinstance(hid, str) and hid.strip()):
            d["id"] = f"hyp-{i + 1}"
        if "priority" not in d:
            d["priority"] = "MEDIUM"
        if "expected_outcome" not in d:
            d["expected_outcome"] = ""
        out.append(d)
    return out


class EpistemicInjectionConfig(BaseModel):
    """Controls automatic literature and code-repository injection (Capa 2)."""

    enabled: bool = False
    n_papers_to_fetch: int = 20
    n_repos_to_fetch: int = 5
    poison_pills: list[dict[str, Any]] = Field(default_factory=list)


class ComputeConfig(BaseModel):
    """Describes available compute resources and delegation thresholds."""

    local_gpu_available: bool = False
    local_gpu_memory_gb: float = 0
    colab_mcp_enabled: bool = False
    delegate_threshold_gb: float = 12.0


class QualityGatesConfig(BaseModel):
    """Defines quantitative thresholds the pipeline must meet before publishing."""

    target_metric: str = ""
    higher_is_better: bool = True
    sota_baseline_value: float = 0.0
    breakthrough_margin: float = 0.02
    replication_tolerance: float = 0.01
    require_statistical_significance: bool = True
    #: ``off`` | ``warn`` | ``block`` — contrasta borrador vs ``replication_tier`` en metrics.
    epistemic_alignment_mode: str = "off"
    #: ``off`` | ``warn`` | ``block`` — exige mención de evaluaciones más allá de memorization si ``replication_fidelity: strict_paper``.
    downstream_metrics_mode: str = "off"


class DebuggingConfig(BaseModel):
    """Limits and behaviour for automated debugging loops."""

    #: Máximo de invocaciones del Cursor CLI ``agent`` por run; si un intento falla, el siguiente recibe stdout/stderr del anterior (hasta este tope). Primer éxito corta el bucle.
    cursor_max_attempts: int = Field(default=3, ge=1, le=20)
    perplexity_max_attempts: int = 2
    generate_human_briefing: bool = True


class SafetyConfig(BaseModel):
    """Hard limits that the pipeline must never exceed."""

    max_total_runtime_minutes: int = 120
    max_cost_usd: float = 5.0
    require_human_approval_before_publish: bool = True
    allow_force_push: bool = False


class AutonomyConfig(BaseModel):
    """Optional limits when ``mode: autonomy`` (goal-forming; scheduler-friendly)."""

    max_cycles: int = Field(default=8, ge=1, le=10_000)
    max_parallel_experiments: int = Field(default=1, ge=1, le=64)
    max_global_tokens: int = Field(default=2_000_000, ge=1)


class ResearchAgentConfig(BaseModel):
    """Opt-in supervisor-style research agent (LangGraph-lite)."""

    enabled: bool = False
    max_concurrent: int = Field(default=2, ge=1, le=8)


class ExperimentRunnerConfig(BaseModel):
    """Post-draft experiments: script generado, micro-entrenamiento HF, o benchmark numpy."""

    #: ``minimal_numpy`` — toy; ``hf_llm_micro`` — datasets+transformers+tiny LM; ``auto`` — elige HF si hay torch.
    profile: str = "minimal_numpy"
    #: Si existe ``entrypoint``, ejecutarlo antes que los perfiles integrados.
    prefer_generated_script: bool = True
    entrypoint: str = "outputs/code/run_experiment.py"
    hf_model_id: str = "sshleifer/tiny-gpt2"
    hf_dataset_id: str = "wikitext"
    hf_dataset_config: str = "wikitext-2-raw-v1"
    hf_text_field: str = "text"
    max_train_steps: int = Field(default=12, ge=1, le=100_000)
    max_samples: int = Field(default=2000, ge=10, le=2_000_000)
    seed: int = 42
    subprocess_timeout_sec: int = Field(default=7200, ge=60, le=86400)
    #: Escribir ``outputs/code/colab_llm_experiment.ipynb`` para GPU en Colab (subir y ejecutar).
    write_colab_notebook: bool = True
    #: Si se rellena, tiene prioridad sobre ``hf_dataset_id``/config (parseo de ``huggingface.co/datasets/...``).
    hf_dataset_url: str | None = None
    #: Si se rellena, tiene prioridad sobre ``hf_model_id`` (parseo de ``huggingface.co/<modelo>``).
    hf_model_url: str | None = None
    #: ``git clone`` superficial antes del script/HF (solo github.com / gitlab.com).
    code_repo_url: str | None = None
    code_repo_branch: str | None = None
    code_repo_clone_depth: int = Field(default=1, ge=1, le=10)
    clone_timeout_sec: int = Field(default=600, ge=30, le=7200)
    #: Buscar en ``draft_paper.md`` el primer enlace HF dataset + GitHub si los campos URL están vacíos.
    prefer_urls_from_draft: bool = False
    #: Si ``enable_experiment_runner`` y ``metrics.json`` indica fallo, el pipeline termina en error (no “éxito” aparente).
    block_pipeline_on_failure: bool = True
    #: Si el perfil pide ``hf_llm_micro`` pero faltan dependencias (ImportError), ejecutar benchmark ``minimal_numpy`` y seguir (metrics indica fallback).
    fallback_minimal_on_hf_import_error: bool = True
    #: Si True, no ejecuta el experimento antes del quality check; corre el bucle post-Cursor (experimento → validación determinista → Cursor opcional).
    iteration_after_cursor: bool = False
    #: Rondas máximas en el bucle post-Cursor (cada ronda puede incluir un reintento de Cursor).
    iteration_max_rounds: int = Field(default=3, ge=1, le=10)
    #: Tras fallo de validación determinista, una pregunta corta a Perplexity (si hay cupo de llamadas).
    iteration_perplexity_on_fail: bool = False
    #: Cotas opcionales sobre rutas en ``metrics.json``, p. ej. ``metrics.train_loss: {min: 0, max: 100}``.
    deterministic_metrics_bounds: dict[str, Any] | None = None

    @field_validator("profile")
    @classmethod
    def _profile_ok(cls, value: str) -> str:
        v = (value or "minimal_numpy").strip().lower()
        allowed = {"minimal_numpy", "hf_llm_micro", "auto"}
        if v not in allowed:
            msg = f"experiment_runner.profile must be one of {sorted(allowed)}"
            raise ValueError(msg)
        return v


class ExperimentRunnerPatch(BaseModel):
    """Partial merge for ``Mission.experiment_runner`` (API PATCH)."""

    model_config = ConfigDict(extra="forbid")

    profile: str | None = None
    prefer_generated_script: bool | None = None
    entrypoint: str | None = None
    hf_model_id: str | None = None
    hf_dataset_id: str | None = None
    hf_dataset_config: str | None = None
    hf_text_field: str | None = None
    max_train_steps: int | None = Field(default=None, ge=1, le=100_000)
    max_samples: int | None = Field(default=None, ge=10, le=2_000_000)
    seed: int | None = None
    subprocess_timeout_sec: int | None = Field(default=None, ge=60, le=86400)
    write_colab_notebook: bool | None = None
    hf_dataset_url: str | None = None
    hf_model_url: str | None = None
    code_repo_url: str | None = None
    code_repo_branch: str | None = None
    code_repo_clone_depth: int | None = Field(default=None, ge=1, le=10)
    clone_timeout_sec: int | None = Field(default=None, ge=30, le=7200)
    prefer_urls_from_draft: bool | None = None
    block_pipeline_on_failure: bool | None = None
    fallback_minimal_on_hf_import_error: bool | None = None
    iteration_after_cursor: bool | None = None
    iteration_max_rounds: int | None = Field(default=None, ge=1, le=10)
    iteration_perplexity_on_fail: bool | None = None
    deterministic_metrics_bounds: dict[str, Any] | None = None

    @field_validator("profile")
    @classmethod
    def _profile_patch_ok(cls, value: str | None) -> str | None:
        if value is None:
            return None
        v = value.strip().lower()
        allowed = {"minimal_numpy", "hf_llm_micro", "auto"}
        if v not in allowed:
            msg = f"experiment_runner.profile must be one of {sorted(allowed)}"
            raise ValueError(msg)
        return v


# ---------------------------------------------------------------------------
# Mission model (v1 + v2 fields)
# ---------------------------------------------------------------------------


class Mission(BaseModel):
    """Single human-edited mission file (Capa 1).

    v1 fields are preserved at the top level.  v2 adds optional nested
    configuration blocks — all default to safe no-op values so existing
    mission files continue to load without modification.

    ``mission_version``:
      - ``1`` — legacy behaviour (default when omitted).
      - ``2`` — stricter contract: requires ``enable_quality_check`` and non-empty ``paper_target``.
    """

    mission_version: int = Field(default=1, ge=1, le=2)

    #: ``standard`` (default) or ``autonomy`` (goal-forming / scheduler-aware; optional).
    mode: str = Field(default="standard")
    autonomy: AutonomyConfig | None = None

    # -- v1 fields (unchanged) ------------------------------------------------
    topic: str
    paper_target: str = "generic venue"
    #: LLM provider: ``perplexity`` (default), ``xiaomi_mimo``, or ``mistral``.
    provider: str = "perplexity"
    research_agent: ResearchAgentConfig = Field(default_factory=ResearchAgentConfig)
    sections_needed: list[str] = Field(
        default_factory=lambda: [
            "related_work",
            "sota",
            "gaps",
            "methodology",
            "experiments",
        ]
    )
    max_perplexity_calls: int = Field(default=8, ge=1, le=64)
    code_needed: bool = False
    #: If True, after assembly the pipeline runs the built-in toy benchmark and writes ``outputs/metrics.json`` (numpy; see ``paper-pipeline[experiments]``).
    enable_experiment_runner: bool = False
    #: Perfil de experimento (script HF / numpy / auto); ver ``ExperimentRunnerConfig``.
    experiment_runner: ExperimentRunnerConfig = Field(default_factory=ExperimentRunnerConfig)
    notion_page_id: str | None = None
    model: str = "best"
    language: str = "en-US"
    output_dir: str = "outputs"
    enable_notion: bool = False
    enable_quality_check: bool = True
    enable_cursor_cli: bool = False
    #: Si True (o env ``PAPER_PIPELINE_CURSOR_CLI_OPTIONAL``), un fallo del agente no aborta el run completo (default: no bloquear).
    cursor_cli_optional: bool = True
    cursor_cli_prompt_path: str | None = None
    cursor_cli_cwd: str | None = None
    #: Reuse one Perplexity thread for all section asks (and optional quality check) so prior turns stay in context.
    single_thread_perplexity: bool = False
    #: If True, threads are saved to Perplexity library (visible in web history). If False, incognito — often no history entry.
    save_perplexity_to_library: bool = True
    #: Fase de réplica formal: ``A`` (cercana al paper), ``B`` (extensión), ``AB``, o vacío.
    replication_phase: str = ""
    #: Modelos/métricas ancladas al paper (Fase A).
    replication_phase_a_scope: str = ""
    #: Extensión pragmática (Fase B), p. ej. SLMs; no confundir con réplica del claim principal.
    replication_phase_b_scope: str = ""
    #: ``strict_paper`` exige alineación explícita; ``extension_exploratory`` relaja gates epistémicos.
    replication_fidelity: str = ""

    # -- v2 nested config blocks ----------------------------------------------
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    epistemic_injection: EpistemicInjectionConfig = Field(
        default_factory=EpistemicInjectionConfig
    )
    compute: ComputeConfig = Field(default_factory=ComputeConfig)
    quality_gates: QualityGatesConfig = Field(default_factory=QualityGatesConfig)
    debugging: DebuggingConfig = Field(default_factory=DebuggingConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)

    # -- v2 convenience feature flags -----------------------------------------
    enable_epistemic_injection: bool = False
    enable_degradation_monitor: bool = False
    enable_skill_orchestrator: bool = False
    #: Post-run hypervisor triage (tiers + triage_report.json) when outputs/metrics.json exists.
    enable_hypervisor_triage: bool = False
    #: Si se define (no vacío), restringe los ejecutables del batch ``paper-parallel`` a estos prefijos
    #: (basenames, p. ej. ``python``, ``pytest``). Si es ``None``, se usa ``PAPER_PIPELINE_PARALLEL_CMD_PREFIXES`` o el default.
    parallel_allowed_command_prefixes: list[str] | None = None

    @field_validator("mode")
    @classmethod
    def _mode_ok(cls, value: str) -> str:
        v = (value or "standard").strip().lower()
        if v not in ("standard", "autonomy"):
            msg = "mode must be 'standard' or 'autonomy'"
            raise ValueError(msg)
        return v

    @field_validator("provider")
    @classmethod
    def _provider_ok(cls, value: str) -> str:
        v = (value or "perplexity").strip().lower()
        if v not in ("perplexity", "xiaomi_mimo", "mistral"):
            msg = "provider must be 'perplexity', 'xiaomi_mimo', or 'mistral'"
            raise ValueError(msg)
        return v

    @field_validator("sections_needed", mode="before")
    @classmethod
    def _strip_sections(cls, value: Any) -> list[str]:
        if value is None:
            return [
                "related_work",
                "sota",
                "gaps",
                "methodology",
                "experiments",
            ]
        if isinstance(value, list):
            return [str(s).strip() for s in value if str(s).strip()]
        msg = "sections_needed must be a list of strings"
        raise TypeError(msg)


def load_mission(path: Path | str) -> Mission:
    """Load mission from a Markdown file with YAML frontmatter."""

    p = Path(path)
    raw = p.read_text(encoding="utf-8")

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            front = parts[1].strip()
            data = yaml.safe_load(front) or {}
            if not isinstance(data, dict):
                msg = "YAML frontmatter must be a mapping"
                raise ValueError(msg)
            from paper_pipeline.config.mission_contract import normalize_mission_dict

            return Mission.model_validate(normalize_mission_dict(data))

    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        msg = "mission file must be YAML frontmatter or a YAML document"
        raise ValueError(msg)
    from paper_pipeline.config.mission_contract import normalize_mission_dict

    return Mission.model_validate(normalize_mission_dict(data))


def save_mission(mission: Mission, path: Path) -> None:
    """Write mission as Markdown with YAML frontmatter (compatible with load_mission)."""

    data = mission.model_dump(mode="python")
    yaml_body = yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    path.write_text(f"---\n{yaml_body}---\n", encoding="utf-8")
