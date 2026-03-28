"""Contrato de capacidad empírica y tier de réplica (visión 03-27)."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Tier estable para orquestación y gates
TIER_FAILED = "failed"
TIER_PLANNING_ONLY = "planning_only"
TIER_PARTIAL_INFRASTRUCTURE = "partial_infrastructure"
TIER_FULL_EMPIRICAL = "full_empirical"


def _read_metrics_dict(out: Path) -> dict[str, Any] | None:
    p = out / "metrics.json"
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def infer_replication_tier(data: dict[str, Any]) -> str:
    """Deriva ``replication_tier`` desde un payload ``metrics.json``."""

    ec = data.get("exit_code")
    try:
        ec_int = int(ec) if ec is not None else None
    except (TypeError, ValueError):
        ec_int = None
    if ec_int is not None and ec_int != 0:
        return TIER_FAILED

    er = data.get("experiment_runner")
    er = er if isinstance(er, dict) else {}
    status = str(er.get("status") or "").lower()
    if status == "skipped":
        reason = str(er.get("reason") or "")
        if "numpy" in reason.lower():
            return TIER_PLANNING_ONLY
        return TIER_PARTIAL_INFRASTRUCTURE

    if er.get("fallback_from_hf_import") is True:
        return TIER_PARTIAL_INFRASTRUCTURE

    name = str(er.get("name") or "")
    if name == "numpy_linear_synthetic":
        return TIER_PARTIAL_INFRASTRUCTURE

    prof = str(er.get("profile") or "").lower()
    if prof == "hf_llm_micro" and status == "ok":
        return TIER_FULL_EMPIRICAL

    if er.get("status") == "ok" and name and name != "numpy_linear_synthetic":
        # Script de usuario u otro perfil que escribió nombre propio
        return TIER_FULL_EMPIRICAL

    if er.get("status") == "ok":
        return TIER_FULL_EMPIRICAL

    return TIER_PARTIAL_INFRASTRUCTURE


def build_capability_contract(data: dict[str, Any]) -> dict[str, Any]:
    """Lista qué capacidades el run preserva respecto a una réplica tipo K-FAC / LM."""

    tier = infer_replication_tier(data)
    er = data.get("experiment_runner")
    er = er if isinstance(er, dict) else {}
    fb = er.get("fallback_from_hf_import") is True
    name = str(er.get("name") or "")
    prof = str(er.get("profile") or "").lower()

    hf_load: str
    if tier == TIER_FAILED:
        hf_load = "unknown"
    elif prof == "hf_llm_micro" and not fb:
        hf_load = "available"
    elif fb or name == "numpy_linear_synthetic" or tier == TIER_PLANNING_ONLY:
        hf_load = "unavailable"
    elif er.get("status") == "ok" and name:
        hf_load = "unknown"
    else:
        hf_load = "unknown"

    kfac = "unavailable"
    grad = "unavailable"
    full_rep = "unavailable"
    if tier == TIER_FULL_EMPIRICAL and prof == "hf_llm_micro" and not fb:
        grad = "available"
        hf_load = "available"
    elif tier == TIER_FULL_EMPIRICAL and er.get("status") == "ok" and name and "kfac" in name.lower():
        kfac = "available"
        grad = "available"

    summary_parts: list[str] = []
    if tier == TIER_PARTIAL_INFRASTRUCTURE:
        summary_parts.append(
            "Benchmark integrado mínimo o fallback HF→numpy: no valida recolección K-FAC ni réplica del paper."
        )
    elif tier == TIER_PLANNING_ONLY:
        summary_parts.append("Sin numpy: sin benchmark empírico local.")
    elif tier == TIER_FAILED:
        summary_parts.append("Métricas con error: sin validez empírica.")
    elif prof == "hf_llm_micro":
        summary_parts.append(
            "Micro-entrenamiento HF ejecutado; no implica réplica completa del paper citado (ver notas en metrics)."
        )
    else:
        summary_parts.append("Salida de script/métricas presente; revisar notas para alineación con el paper.")

    return {
        "hf_model_load": hf_load,
        "kfac_statistics": kfac,
        "gradient_collection": grad,
        "full_paper_replication": full_rep,
        "human_summary": " ".join(summary_parts).strip(),
    }


def enrich_metrics_json(out: Path) -> dict[str, Any] | None:
    """Añade ``replication_tier``, ``capability_contract`` y normaliza ``experiment_runner``."""

    data = _read_metrics_dict(out)
    if not data:
        return None
    tier = infer_replication_tier(data)
    contract = build_capability_contract(data)
    data["replication_tier"] = tier
    data["capability_contract"] = contract
    er = data.get("experiment_runner")
    if isinstance(er, dict) and "replication_tier" not in er:
        er2 = dict(er)
        er2["replication_tier"] = tier
        data["experiment_runner"] = er2
    try:
        (out / "metrics.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.warning("enrich_metrics_json: could not write metrics.json: %s", exc)
        return None
    return data


def read_replication_tier_from_out(out: Path) -> str:
    data = _read_metrics_dict(out)
    if not data:
        return "unknown"
    if "replication_tier" in data and isinstance(data["replication_tier"], str):
        return data["replication_tier"]
    return infer_replication_tier(data)


def compute_empirical_fingerprint(out: Path) -> str:
    """Huella corta para invalidar resume si cambia el modo empírico."""

    data = _read_metrics_dict(out)
    if not data:
        return ""
    tier = read_replication_tier_from_out(out)
    er = data.get("experiment_runner")
    er = er if isinstance(er, dict) else {}
    fb = bool(er.get("fallback_from_hf_import"))
    prof = str(er.get("profile") or "")
    raw = f"{tier}|{fb}|{prof}|{er.get('name') or ''}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def strip_empirical_dependent_resume_steps(state: Any) -> None:
    state.completed_steps = [
        s
        for s in state.completed_steps
        if s not in ("step:quality_check", "step:cursor_cli")
        and not (isinstance(s, str) and s.startswith("perplexity:"))
    ]


def maybe_invalidate_on_empirical_fingerprint_change(
    state: Any,
    state_path: Path,
    out: Path,
) -> None:
    """Si ``metrics.json`` cambió de modo respecto al último run guardado, invalida pasos dependientes."""

    new_fp = compute_empirical_fingerprint(out)
    old_fp = getattr(state, "empirical_fingerprint", "") or ""
    if not new_fp or not old_fp or new_fp == old_fp:
        return
    strip_empirical_dependent_resume_steps(state)
    state.save(state_path)
    logger.warning(
        "empirical_fingerprint changed (%s -> %s): invalidated perplexity:* and quality_check",
        old_fp,
        new_fp,
    )
