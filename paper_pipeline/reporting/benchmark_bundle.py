"""Aggregate deterministic benchmark stats for preprint tables and ``benchmark_bundle.json`` (no network)."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
from paper_pipeline.agent_eval.eval_runner import run_all
from paper_pipeline.reporting.case_study_trace import (
    build_case_study_trace,
    build_minimal_safety_usecase_trace,
)


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts or not isinstance(ts, str):
        return None
    s = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def ledger_phase_durations_seconds(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Per-phase wall time in seconds using ``started_at``/``ended_at`` when present;
    falls back to previous phase end as start when ``started_at`` is null.
    """
    started = _parse_iso(ledger.get("started_at"))
    phases = ledger.get("phases")
    if not isinstance(phases, list):
        return []
    out: list[dict[str, Any]] = []
    prev_end = started
    for p in phases:
        if not isinstance(p, dict):
            continue
        name = p.get("name")
        st = _parse_iso(p.get("started_at"))
        en = _parse_iso(p.get("ended_at"))
        start = st or prev_end
        if start is None or en is None:
            continue
        sec = max(0.0, (en - start).total_seconds())
        out.append({"phase": name, "seconds": round(sec, 3), "status": p.get("status")})
        prev_end = en
    return out


def build_benchmark_bundle(
    *,
    repo_root: Path,
    case_study_outputs: Path | None = None,
    agent_eval_report_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Single JSON blob for preprint: agent_eval report + optional case_study_trace + ledger stats.

    Intended for supplementary tables / honest benchmarking (CI governance, not LLM quality).

    If ``agent_eval_report_payload`` is provided (e.g. from a single ``run_all`` in the caller),
    the harness is **not** run again.
    """
    repo_root = repo_root.resolve()
    if agent_eval_report_payload is not None:
        agent_payload = agent_eval_report_payload
    else:
        with tempfile.TemporaryDirectory() as td:
            report = run_all(Path(td))
        agent_payload = scorecard_to_stable_dict(report)

    cs_path = case_study_outputs
    if cs_path is None:
        default_m = repo_root / "data" / "missions" / "4f6715a65f4c" / "outputs"
        if default_m.is_dir() and (default_m / "run_ledger.json").is_file():
            trace = build_case_study_trace(default_m)
        else:
            trace = build_minimal_safety_usecase_trace(repo_root)
    else:
        trace = build_case_study_trace(cs_path.resolve())

    ledger_path = None
    if case_study_outputs and (case_study_outputs / "run_ledger.json").is_file():
        ledger_path = case_study_outputs / "run_ledger.json"
    elif (repo_root / "data" / "missions" / "4f6715a65f4c" / "outputs" / "run_ledger.json").is_file():
        ledger_path = repo_root / "data" / "missions" / "4f6715a65f4c" / "outputs" / "run_ledger.json"

    phase_stats: list[dict[str, Any]] = []
    wall_total_s: float | None = None
    if ledger_path and ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            if isinstance(ledger, dict):
                phase_stats = ledger_phase_durations_seconds(ledger)
                t0 = _parse_iso(ledger.get("started_at"))
                t1 = _parse_iso(ledger.get("ended_at"))
                if t0 and t1:
                    wall_total_s = round((t1 - t0).total_seconds(), 3)
        except (OSError, json.JSONDecodeError):
            pass

    per_scenario = []
    for r in agent_payload.get("results", []) or []:
        if not isinstance(r, dict):
            continue
        per_scenario.append(
            {
                "scenario_id": r.get("scenario_id"),
                "target": r.get("target"),
                "passed": r.get("passed"),
            }
        )

    return {
        "schema_version": 1,
        "kind": "benchmark_bundle",
        "note": "Deterministic harness + mission trace; not an ML accuracy benchmark.",
        "agent_eval": {
            "scenarios_run": agent_payload.get("scenarios_run"),
            "scenarios_passed": agent_payload.get("scenarios_passed"),
            "scorecard": agent_payload.get("scorecard"),
            "per_scenario": per_scenario,
        },
        "case_study_trace": trace,
        "mission_ledger": {
            "wall_clock_total_s": wall_total_s,
            "phase_durations_s": phase_stats,
        },
    }


def benchmark_bundle_to_markdown_table(bundle: dict[str, Any]) -> str:
    """Human-readable Markdown: scenario table + one block for ledger/triage (for LaTeX copy-paste)."""

    lines: list[str] = [
        "<!-- Generated from benchmark_bundle.json — deterministic harness, not ML accuracy. -->",
        "",
        "## Agent eval (per scenario)",
        "",
        "| scenario_id | target | passed |",
        "|-------------|--------|--------|",
    ]
    for row in bundle.get("agent_eval", {}).get("per_scenario", []) or []:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("scenario_id", "")).replace("|", "\\|")
        tgt = str(row.get("target", "")).replace("|", "\\|")
        ok = row.get("passed")
        lines.append(f"| `{sid}` | {tgt} | {ok} |")

    lines.extend(["", "## Mission ledger (reference trace)", ""])
    ml = bundle.get("mission_ledger") or {}
    w = ml.get("wall_clock_total_s")
    lines.append(f"- **Wall clock (s):** {w}")
    lines.append("- **Phase durations:**")
    for p in ml.get("phase_durations_s") or []:
        if isinstance(p, dict):
            lines.append(f"  - `{p.get('phase')}`: {p.get('seconds')} s")

    cs = bundle.get("case_study_trace") or {}
    if isinstance(cs, dict):
        lines.extend(["", "## Case study trace (summary)", ""])
        lines.append(f"- **Claims extracted:** {cs.get('claims_extracted_count', '—')}")
        td = cs.get("triage") if isinstance(cs.get("triage"), dict) else {}
        pub = cs.get("publish_decision") if isinstance(cs.get("publish_decision"), dict) else {}
        tier_val = td.get("tier") if td else pub.get("triage_tier")
        lines.append(f"- **Triage tier:** {tier_val}")
        ms = cs.get("metrics_summary") if isinstance(cs.get("metrics_summary"), dict) else {}
        lines.append(f"- **Replication tier:** {ms.get('replication_tier', '—')}")

    return "\n".join(lines) + "\n"


def main() -> None:
    """CLI: write benchmark_bundle JSON (no matplotlib)."""

    import argparse
    import sys

    p = argparse.ArgumentParser(description="Write benchmark_bundle.json (agent_eval + mission trace).")
    p.add_argument("-o", "--out", type=Path, required=True, help="Output .json path")
    p.add_argument("--repo-root", type=Path, default=None, help="Repo root (default: cwd)")
    p.add_argument(
        "--case-study-outputs",
        type=Path,
        default=None,
        metavar="OUTPUTS_DIR",
        help="Mission outputs/ (default: reference mission or P2 fallback)",
    )
    args = p.parse_args()
    repo = (args.repo_root or Path.cwd()).resolve()
    bundle = build_benchmark_bundle(repo_root=repo, case_study_outputs=args.case_study_outputs)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.out.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
