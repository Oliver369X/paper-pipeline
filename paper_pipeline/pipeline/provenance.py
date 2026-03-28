"""Resumen operativo post-pipeline (diff entre corridas, cockpit)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def write_pipeline_provenance_json(output_dir: Path) -> Path:
    """Escribe ``outputs/pipeline_provenance.json`` con tier, CLI y fallback (best-effort)."""

    output_dir = Path(output_dir)
    metrics = _read_json(output_dir / "metrics.json")
    cursor_d = _read_json(output_dir / "cursor_cli_diagnostics.json")
    exp_d = _read_json(output_dir / "experiment_diagnostics.json")
    prompt_last = output_dir / "cursor_cli_prompt_last.txt"

    er = metrics.get("experiment_runner") if metrics else None
    er = er if isinstance(er, dict) else {}
    fb = bool(er.get("fallback_from_hf_import"))

    payload = {
        "schema_version": 1,
        "replication_tier": metrics.get("replication_tier") if metrics else None,
        "capability_contract": metrics.get("capability_contract") if metrics else None,
        "experiment_runner_fallback_from_hf_import": fb,
        "cursor_cli": {
            "exit_code": cursor_d.get("exit_code") if cursor_d else None,
            "stderr_preview": (cursor_d.get("stderr_truncated") or "")[:400] if cursor_d else None,
        },
        "experiment_diagnostics": {
            "replication_tier": exp_d.get("replication_tier") if exp_d else None,
            "degraded_success": exp_d.get("degraded_success") if exp_d else None,
        },
        "cursor_cli_prompt_last_path": str(prompt_last.name) if prompt_last.is_file() else None,
    }
    p = output_dir / "pipeline_provenance.json"
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
