"""Validación determinista de ``outputs/metrics.json`` (sanidad numérica y cotas opcionales)."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _get_path(data: Any, dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted)
        cur = cur[part]
    return cur


def _collect_float_issues(obj: Any, prefix: str, issues: list[str]) -> None:
    if isinstance(obj, float):
        if not math.isfinite(obj):
            issues.append(f"non-finite float at {prefix or 'root'}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _collect_float_issues(v, f"{prefix}.{k}" if prefix else str(k), issues)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _collect_float_issues(v, f"{prefix}[{i}]", issues)


def validate_metrics_deterministic(
    out: Path,
    bounds: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    """Comprueba JSON, ``exit_code == 0``, floats finitos y cotas opcionales.

    ``bounds`` es un mapa ``clave.con.puntos`` → ``{"min": float, "max": float}`` (ambos opcionales).
    """

    reasons: list[str] = []
    p = out / "metrics.json"
    if not p.is_file():
        return False, ["missing outputs/metrics.json"]

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, [f"metrics.json invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return False, ["metrics.json root must be an object"]

    ec = data.get("exit_code")
    if ec is None:
        reasons.append("missing exit_code in metrics.json")
    elif ec != 0:
        reasons.append(f"exit_code must be 0, got {ec}")

    finite_issues: list[str] = []
    _collect_float_issues(data, "", finite_issues)
    reasons.extend(finite_issues)

    if bounds:
        for path, spec in bounds.items():
            if not isinstance(spec, dict):
                reasons.append(f"bound for {path!r} must be an object")
                continue
            try:
                val = _get_path(data, path)
            except KeyError:
                reasons.append(f"bound path not found: {path}")
                continue
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                reasons.append(f"bound path {path} is not numeric (got {type(val).__name__})")
                continue
            v = float(val)
            if "min" in spec and v < float(spec["min"]):
                reasons.append(f"{path}={v} below min {spec['min']}")
            if "max" in spec and v > float(spec["max"]):
                reasons.append(f"{path}={v} above max {spec['max']}")

    ok = len(reasons) == 0
    return ok, reasons


def write_experiment_deterministic_validation(out: Path, ok: bool, reasons: list[str]) -> Path:
    """Escribe ``outputs/validation/experiment_deterministic.json``."""

    vd = out / "validation"
    vd.mkdir(parents=True, exist_ok=True)
    path = vd / "experiment_deterministic.json"
    path.write_text(
        json.dumps({"ok": ok, "reasons": reasons}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path
