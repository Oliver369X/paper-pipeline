"""Bucle post-Cursor: ejecutar experimento, validación determinista, reintentos con Cursor y Perplexity opcional."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from perplexity_webui_scraper import Perplexity

from paper_pipeline.cursor_cli_runner import run_cursor_cli
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.mission import Mission
from .common import build_conversation_config
from .experiment_metrics_validate import validate_metrics_deterministic, write_experiment_deterministic_validation
from .experiment_phase import ExperimentRunnerResult, run_experiment_runner_phase

logger = logging.getLogger(__name__)

HINT_FILE = "experiment_iteration_hint.md"
LOG_JSONL = "experiment_iteration.jsonl"


def _append_jsonl(out: Path, record: dict[str, Any]) -> None:
    p = out / LOG_JSONL
    line = json.dumps(record, ensure_ascii=False) + "\n"
    if p.is_file():
        p.write_text(p.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        p.write_text(line, encoding="utf-8")


def _perplexity_hint_on_failure(
    mission: Mission,
    client: Perplexity,
    out: Path,
    reasons: list[str],
    metrics_snip: str,
) -> str:
    """Una pregunta corta a Perplexity sobre el fallo de validación (si hay cupo)."""

    cfg = build_conversation_config(mission)
    conv = client.create_conversation(cfg)
    body = (
        "Eres un asistente técnico. El pipeline de investigación ejecutó un experimento y la validación "
        "determinista de métricas falló. Responde en 2–6 viñetas qué podría corregirse en el código o en "
        "el diseño del experimento (sin inventar números que no estén en el contexto).\n\n"
        f"Motivos de fallo:\n{json.dumps(reasons, ensure_ascii=False, indent=2)}\n\n"
        f"Extracto de metrics.json (truncado):\n{metrics_snip[:12000]}\n"
    )
    conv.ask(body)
    return (conv.answer or "").strip()


def run_post_cursor_experiment_iteration(
    mission: Mission,
    mission_path: Path,
    out: Path,
    plog: PipelineLogger,
    client: Perplexity,
    calls_used: int,
) -> tuple[ExperimentRunnerResult, int]:
    """Tras Cursor: hasta N rondas de (experimento → validar → pista → Cursor opcional).

    Requiere ``experiment_runner.iteration_after_cursor`` y experiment runner habilitado.
    """

    cfg = mission.experiment_runner
    max_rounds = cfg.iteration_max_rounds
    bounds = cfg.deterministic_metrics_bounds

    last_res = ExperimentRunnerResult(ok=False, exit_code=1, reason="not started")

    for round_idx in range(1, max_rounds + 1):
        plog.step_start(
            "experiment_iteration",
            round=round_idx,
            max_rounds=max_rounds,
        )
        last_res = run_experiment_runner_phase(mission, out, plog, mission_path=mission_path)

        metrics_snip = ""
        mp = out / "metrics.json"
        if mp.is_file():
            metrics_snip = mp.read_text(encoding="utf-8")

        ok_det, reasons = validate_metrics_deterministic(out, bounds)
        write_experiment_deterministic_validation(out, ok_det, reasons)

        pass_all = last_res.ok and ok_det
        _append_jsonl(
            out,
            {
                "round": round_idx,
                "experiment_ok": last_res.ok,
                "deterministic_ok": ok_det,
                "reasons": reasons,
                "replication_tier": last_res.replication_tier,
            },
        )

        if pass_all:
            plog.step_ok("experiment_iteration", round=round_idx, deterministic=True)
            return last_res, calls_used

        hint_lines = [
            f"# Experiment iteration — round {round_idx}/{max_rounds}",
            "",
            "## Pipeline experiment result",
            f"- ok: {last_res.ok}",
            f"- reason: {last_res.reason}",
            f"- replication_tier: {last_res.replication_tier}",
            "",
            "## Deterministic validation",
            f"- ok: {ok_det}",
            f"- reasons: {reasons}",
            "",
            "Fix `outputs/code/` (especially `run_experiment.py` if used) so metrics pass; keep dependencies minimal.",
        ]

        ppl_digest = ""
        if cfg.iteration_perplexity_on_fail and calls_used < mission.max_perplexity_calls:
            try:
                ppl_digest = _perplexity_hint_on_failure(mission, client, out, reasons, metrics_snip)
                calls_used += 1
                hint_lines.extend(["", "## Perplexity (optional hint)", "", ppl_digest])
            except Exception as exc:  # noqa: BLE001
                logger.exception("Perplexity iteration hint failed")
                hint_lines.extend(["", "## Perplexity failed", str(exc)])

        hint_path = out / HINT_FILE
        hint_path.write_text("\n".join(hint_lines), encoding="utf-8")

        if round_idx >= max_rounds:
            plog.step_error(
                "experiment_iteration",
                error="exhausted_rounds",
                detail=f"round {round_idx}/{max_rounds}",
            )
            break

        if not (mission.code_needed and mission.enable_cursor_cli):
            logger.warning("experiment_iteration: no cursor for retry (code_needed and enable_cursor_cli required)")
            break

        plog.step_start("step:cursor_cli", iteration_round=round_idx + 1)
        mission_dir = mission_path.resolve().parent
        cwd = Path(mission.cursor_cli_cwd).resolve() if mission.cursor_cli_cwd else mission_dir

        follow = (
            "The deterministic experiment validation failed. Read outputs/experiment_iteration_hint.md "
            "and outputs/metrics.json; fix outputs/code/ so the next run produces valid metrics "
            "(exit_code 0 and satisfy validation). Summarize changes at the end."
        )
        cli_code = run_cursor_cli(
            cwd=cwd,
            output_dir=out,
            mission=mission,
            prompt=follow,
            prompt_file=None,
            dry_run=False,
            pipeline_log=plog,
        )
        if cli_code != 0:
            plog.step_error("step:cursor_cli", error="iteration_cursor_failed", exit_code=cli_code)
            break
        plog.step_ok("step:cursor_cli", iteration_round=round_idx + 1)

    return last_res, calls_used


def should_defer_experiment_until_after_cursor(mission: Mission) -> bool:
    """True si el experimento integrado se ejecuta solo en el bucle post-Cursor."""

    if not mission.enable_experiment_runner:
        return False
    if not (mission.code_needed and mission.enable_cursor_cli):
        return False
    return bool(mission.experiment_runner.iteration_after_cursor)
