"""Markdown audit table for preprint numbers (reads mission JSON from disk; no network)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _read_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def wall_clock_seconds(ledger: dict) -> float | None:
    t0 = ledger.get("started_at")
    t1 = ledger.get("ended_at")
    if not t0 or not t1:
        return None
    a = datetime.fromisoformat(str(t0).replace("Z", "+00:00"))
    b = datetime.fromisoformat(str(t1).replace("Z", "+00:00"))
    return max(0.0, (b - a).total_seconds())


def run_audit(
    *,
    repo_root: Path,
    mission_outputs: Path,
    claims_path: Path | None = None,
) -> str:
    mission_outputs = mission_outputs.resolve()
    claims_p = claims_path or (mission_outputs / "evidence" / "claims.json")
    try:
        claims_rel = claims_p.resolve().relative_to(repo_root.resolve())
    except ValueError:
        claims_rel = claims_p

    lines: list[str] = [
        "## Abstract number audit (generated)",
        "",
        "| Claim / number | Value (this snapshot) | Source path | Reproducibility class |",
        "|----------------|------------------------|-------------|----------------------|",
    ]

    ledger = _read_json(mission_outputs / "run_ledger.json")
    if isinstance(ledger, dict):
        wc = wall_clock_seconds(ledger)
        rid = ledger.get("run_id", "—")
        wc_s = f"{wc:.3f} s" if wc is not None else "—"
        lines.append(
            f"| Wall clock (single run) | {wc_s} (run_id `{rid}`) | `run_ledger.json` started_at/ended_at | **Snapshot** - varies with CPU, network, Perplexity, Cursor |"
        )
        phases = ledger.get("phases")
        n_ph = len(phases) if isinstance(phases, list) else 0
        lines.append(
            f"| Ledger phases recorded | {n_ph} | `run_ledger.json` phases | Same snapshot; re-run may differ |"
        )
    else:
        lines.append("| Wall clock | — | run_ledger missing | — |")

    claims = _read_json(claims_p)
    n_claims = len(claims) if isinstance(claims, list) else 0
    lines.append(
        f"| Heuristic claim candidates | {n_claims} | `{claims_rel.as_posix()}` | **Snapshot** - depends on draft text / LLM path |"
    )

    tri = _read_json(mission_outputs / "triage" / "triage_report.json")
    if isinstance(tri, dict):
        tier = tri.get("tier")
        label = tri.get("label", "—")
        lines.append(
            f"| Triage tier | {tier} ({label}) | `triage/triage_report.json` | **Snapshot** - can change if metrics or gates change |"
        )

    met = _read_json(mission_outputs / "metrics.json")
    if isinstance(met, dict):
        rt = met.get("replication_tier", "—")
        lines.append(
            f"| Replication tier | `{rt}` | `metrics.json` | **Snapshot** - `planning_only` if numpy/HF stack unavailable |"
        )

    lines.extend(
        [
            "| agent_eval 12/12 @ 1.0 | (run harness) | `python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json` | **Deterministic**, no network |",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
