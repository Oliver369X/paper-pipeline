"""Optional post-assembly phase: script usuario, HF micro-train, o benchmark numpy → ``metrics.json``."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from paper_pipeline.experiments.minimal_benchmark import run_minimal_benchmark, write_experiment_error_metrics
from paper_pipeline.experiments.replication import augment_experiment_config_from_draft
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.experiment_contracts import (
    enrich_metrics_json,
    read_replication_tier_from_out,
)

logger = logging.getLogger(__name__)

TIER_NOT_RUN = "not_run"


def read_metrics_exit_code(out: Path) -> int | None:
    """Lee ``exit_code`` de ``outputs/metrics.json`` si existe."""

    p = out / "metrics.json"
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "exit_code" in data:
            return int(data["exit_code"])
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None
    return None


@dataclass(frozen=True)
class ExperimentRunnerResult:
    """Resultado del bloque empírico integrado (para orquestación y ledger)."""

    ok: bool
    exit_code: int
    reason: str | None = None
    replication_tier: str = "unknown"


def _metrics_exists(out: Path) -> bool:
    return (out / "metrics.json").is_file()


def _result_from_metrics(out: Path, *, default_reason: str | None = None) -> ExperimentRunnerResult:
    enrich_metrics_json(out)
    ec = read_metrics_exit_code(out)
    tier = read_replication_tier_from_out(out)
    if ec is None:
        return ExperimentRunnerResult(
            ok=False,
            exit_code=1,
            reason=default_reason or "missing metrics.json",
            replication_tier=tier,
        )
    ok = ec == 0
    return ExperimentRunnerResult(
        ok=ok,
        exit_code=ec,
        reason=None if ok else f"metrics exit_code={ec}",
        replication_tier=tier,
    )


def run_experiment_runner_phase(
    mission: Mission,
    out: Path,
    plog: PipelineLogger,
    *,
    mission_path: Path,
) -> ExperimentRunnerResult:
    """Ejecuta ``experiment_runner`` según misión. Devuelve :class:`ExperimentRunnerResult` (``ok`` según ``metrics.json``)."""

    if not mission.enable_experiment_runner:
        return ExperimentRunnerResult(ok=True, exit_code=0, replication_tier=TIER_NOT_RUN)

    draft = out / "draft_paper.md"
    cfg = augment_experiment_config_from_draft(mission.experiment_runner, draft)
    root = mission_path.parent.resolve()
    code_parent = out / "code"
    code_parent.mkdir(parents=True, exist_ok=True)

    extra_env: dict[str, str] = {}
    if (cfg.code_repo_url or "").strip():
        try:
            from paper_pipeline.experiments.git_clone import clone_allowed_repo, ensure_git_available

            ensure_git_available()
            clone_dest = clone_allowed_repo(
                cfg.code_repo_url.strip(),
                code_parent,
                branch=cfg.code_repo_branch,
                depth=cfg.code_repo_clone_depth,
                timeout_sec=cfg.clone_timeout_sec,
            )
            extra_env["PAPER_CODE_REPO_DIR"] = str(clone_dest.resolve())
        except Exception as exc:  # noqa: BLE001
            logger.exception("code_repo clone failed")
            write_experiment_error_metrics(out, f"code_repo_url clone: {exc}")
            plog.step_error("experiment_runner", error=f"clone: {exc}")
            return _result_from_metrics(out, default_reason="clone failed")

    step_kw: dict[str, str] = {"output": str(out), "profile": cfg.profile}
    if extra_env.get("PAPER_CODE_REPO_DIR"):
        step_kw["cloned_repo"] = extra_env["PAPER_CODE_REPO_DIR"]
    plog.step_start("experiment_runner", **step_kw)

    script_path = (root / cfg.entrypoint).resolve()
    if cfg.prefer_generated_script and script_path.is_file():
        from paper_pipeline.experiments.user_script_runner import run_user_experiment_script

        code, stdout, stderr = run_user_experiment_script(
            script_path,
            root,
            out,
            timeout_sec=cfg.subprocess_timeout_sec,
            extra_env=extra_env or None,
        )
        if code != 0:
            write_experiment_error_metrics(out, f"user script exit {code}\n{stderr}\n{stdout}")
            plog.step_error("experiment_runner", error=f"user script failed: {code}")
            return _result_from_metrics(out, default_reason=f"user script exit {code}")
        if not _metrics_exists(out):
            write_experiment_error_metrics(
                out,
                "run_experiment.py terminó con código 0 pero falta outputs/metrics.json",
            )
            plog.step_error("experiment_runner", error="missing metrics.json after user script")
            return _result_from_metrics(out, default_reason="missing metrics after user script")
        plog.step_ok("experiment_runner")
        return _result_from_metrics(out)

    resolved = cfg.profile
    if resolved == "auto":
        try:
            import torch  # noqa: F401
        except ImportError:
            resolved = "minimal_numpy"
        else:
            resolved = "hf_llm_micro"

    if resolved == "hf_llm_micro":
        try:
            from paper_pipeline.experiments.colab_export import write_colab_notebook
            from paper_pipeline.experiments.hf_llm_micro import run_hf_llm_micro

            run_hf_llm_micro(out, root, cfg)
            if cfg.write_colab_notebook:
                nb_path = write_colab_notebook(out, cfg)
                plog.step_ok("experiment_runner", colab_notebook=str(nb_path))
            else:
                plog.step_ok("experiment_runner")
        except ImportError as exc:
            logger.warning("hf_llm_micro deps missing: %s", exc)
            if cfg.fallback_minimal_on_hf_import_error:
                logger.info(
                    "experiment_runner: fallback a minimal_numpy (faltan torch/transformers/datasets). "
                    "Instalá: pip install paper-pipeline[llm] para el micro-entrenamiento HF."
                )
                try:
                    run_minimal_benchmark(out)
                    p_metrics = out / "metrics.json"
                    data = json.loads(p_metrics.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        er = data.get("experiment_runner")
                        er_dict = dict(er) if isinstance(er, dict) else {}
                        er_dict["fallback_from_hf_import"] = True
                        er_dict["hf_import_error"] = str(exc)[:800]
                        er_dict["remediation"] = "pip install paper-pipeline[llm]"
                        er_dict["notes"] = (
                            (er_dict.get("notes") or "")
                            + " Perfil hf_llm_micro no ejecutado: dependencias HF ausentes; "
                            "se usó benchmark numpy sintético."
                        ).strip()
                        data["experiment_runner"] = er_dict
                        p_metrics.write_text(
                            json.dumps(data, indent=2, ensure_ascii=False),
                            encoding="utf-8",
                        )
                    plog.step_ok(
                        "experiment_runner",
                        fallback="minimal_numpy_after_hf_import_error",
                    )
                    return _result_from_metrics(out)
                except Exception as fb_exc:  # noqa: BLE001
                    logger.exception("fallback minimal_numpy after HF import error also failed")
                    write_experiment_error_metrics(
                        out,
                        f"{exc}; fallback minimal failed: {fb_exc}; instalá: pip install paper-pipeline[llm]",
                    )
                    plog.step_error("experiment_runner", error="hf_llm_micro_import_fallback_failed")
                    return _result_from_metrics(out, default_reason="hf_llm_micro_import")
            write_experiment_error_metrics(
                out,
                f"{exc}; instalá: pip install paper-pipeline[llm]",
            )
            plog.step_error("experiment_runner", error="hf_llm_micro_import")
            return _result_from_metrics(out, default_reason="hf_llm_micro_import")
        except Exception as exc:  # noqa: BLE001
            logger.exception("hf_llm_micro failed")
            write_experiment_error_metrics(out, str(exc))
            plog.step_error("experiment_runner", error=str(exc))
            return _result_from_metrics(out, default_reason=str(exc))
        return _result_from_metrics(out)

    try:
        run_minimal_benchmark(out)
        plog.step_ok("experiment_runner")
    except Exception as exc:  # noqa: BLE001
        logger.exception("experiment_runner failed")
        write_experiment_error_metrics(out, str(exc))
        plog.step_error("experiment_runner", error=str(exc))
        return _result_from_metrics(out, default_reason=str(exc))
    return _result_from_metrics(out)
