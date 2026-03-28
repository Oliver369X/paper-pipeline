"""Artefactos visibles cuando el bloque empírico no valida una “réplica” local o queda degradado."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.pipeline.experiment_contracts import read_replication_tier_from_out
from paper_pipeline.pipeline.experiment_phase import ExperimentRunnerResult, read_metrics_exit_code


def _experiment_diagnostics_payload(
    out: Path,
    result: ExperimentRunnerResult,
    *,
    mission_topic: str = "",
) -> dict:
    tier = result.replication_tier
    if tier == "unknown":
        tier = read_replication_tier_from_out(out)
    metrics = {}
    try:
        p = out / "metrics.json"
        if p.is_file():
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                metrics = {
                    "replication_tier": raw.get("replication_tier"),
                    "capability_contract": raw.get("capability_contract"),
                }
    except (OSError, json.JSONDecodeError):
        pass
    return {
        "ok": result.ok,
        "exit_code": result.exit_code,
        "reason": result.reason,
        "replication_tier": tier,
        "mission_topic": mission_topic,
        "metrics_exit_code": read_metrics_exit_code(out),
        "metrics_snapshot": metrics,
    }


def write_replication_artifacts(
    out: Path,
    draft_path: Path,
    result: ExperimentRunnerResult,
    *,
    mission_topic: str = "",
) -> None:
    """Escribe ``replication_status.md``, ``experiment_diagnostics.json`` y antepone aviso al borrador (FAILED)."""

    out.mkdir(parents=True, exist_ok=True)
    summary = result.reason or f"exit_code={result.exit_code}"
    diag = _experiment_diagnostics_payload(out, result, mission_topic=mission_topic)
    (out / "experiment_diagnostics.json").write_text(
        json.dumps(diag, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    body = (
        f"# Replication status: FAILED\n\n"
        f"- **Motivo:** {summary}\n"
        f"- **metrics.json:** `outputs/metrics.json` (revisá `exit_code` y `experiment_runner`)\n"
        f"- **Diagnóstico:** `outputs/experiment_diagnostics.json`\n\n"
        "Este borrador puede incluir secciones narrativas y tablas *ejemplo*; **no** sustituyen "
        "una ejecución local exitosa del experiment runner.\n"
    )
    (out / "replication_status.md").write_text(body, encoding="utf-8")
    _prepend_replication_banner_draft(draft_path, summary, kind="FAILED")


def write_degraded_replication_artifacts(
    out: Path,
    draft_path: Path,
    result: ExperimentRunnerResult,
    *,
    mission_topic: str = "",
) -> None:
    """Run exitoso pero tier ``partial_infrastructure`` / ``planning_only``: no réplica K-FAC/paper completa."""

    out.mkdir(parents=True, exist_ok=True)
    tier = result.replication_tier
    if tier in ("unknown", ""):
        tier = read_replication_tier_from_out(out)
    summary = (
        f"replication_tier={tier} — el benchmark integrado no valida recolección K-FAC ni réplica fiel del paper. "
        f"Ver `capability_contract` en `outputs/metrics.json`."
    )
    diag = _experiment_diagnostics_payload(out, result, mission_topic=mission_topic)
    diag["degraded_success"] = True
    (out / "experiment_diagnostics.json").write_text(
        json.dumps(diag, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    body = (
        f"# Replication status: DEGRADED (partial infrastructure)\n\n"
        f"- **Estado:** {summary}\n"
        f"- **metrics.json:** `replication_tier`, `capability_contract`\n"
        f"- **Diagnóstico:** `outputs/experiment_diagnostics.json`\n\n"
        "El pipeline terminó sin error de proceso, pero **no** demuestra una réplica empírica completa del método "
        "del paper (p. ej. covarianzas K-FAC, gradientes/backward). Tratá el borrador como **planning-only** o "
        "extensión hasta instalar dependencias y re-ejecutar.\n"
    )
    (out / "replication_status.md").write_text(body, encoding="utf-8")
    _prepend_replication_banner_draft(draft_path, summary, kind="DEGRADED")


def _prepend_replication_banner_draft(draft_path: Path, summary: str, *, kind: str) -> None:
    if not draft_path.is_file():
        return
    existing = draft_path.read_text(encoding="utf-8")
    tag = f"Replication status: {kind}"
    if tag in existing:
        return
    banner = (
        "\n\n---\n\n"
        f"> **{tag}** — "
        + summary
        + "\n> Ver `outputs/replication_status.md`, `outputs/metrics.json` y `outputs/experiment_diagnostics.json`.\n\n"
    )
    draft_path.write_text(banner + existing, encoding="utf-8")
