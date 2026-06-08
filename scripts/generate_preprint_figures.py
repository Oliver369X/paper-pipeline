#!/usr/bin/env python3
"""
Generate publication-style PNG figures for the preprint bundle under docs/preprint/figures/.

Requires: pip install -e ".[figures]"

Reads live metrics from the agent_eval harness (run_all) — no network.
Writes ``benchmark_bundle.json`` (deterministic stats + optional mission trace).
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
from paper_pipeline.agent_eval.eval_runner import run_all
from paper_pipeline.reporting.benchmark_bundle import (
    benchmark_bundle_to_markdown_table,
    build_benchmark_bundle,
)
from paper_pipeline.reporting.preprint_figures import (
    figure_agent_eval_per_scenario,
    figure_claims_rich,
    figure_ledger_timeline,
    figure_scorecard_axes,
    figure_scorecard_radar,
)


def _legacy_figure_agent_eval_scorecard(out: Path, report_dict: dict) -> None:
    """Original 3-bar summary (kept for backward compatibility)."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
    except ImportError as exc:
        raise SystemExit(
            'matplotlib required: pip install -e ".[figures]"',
        ) from exc

    sc = report_dict.get("scorecard", {})
    spr = float(sc.get("scenario_pass_rate", 0.0))
    sr = sc.get("safety_correct_rate")
    gr = sc.get("goal_selection_correct_rate")
    labels = ["scenario\npass rate", "safety\ncorrect", "goal selection\ncorrect"]
    values = [spr, float(sr) if sr is not None else 0.0, float(gr) if gr is not None else 0.0]
    colors = ["#0d47a1", "#1565c0", "#1976d2"]

    rcParams.update(
        {
            "font.family": "serif",
            "font.size": 11,
            "axes.titlesize": 13,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )
    fig, ax = plt.subplots(figsize=(6.5, 3.8), layout="constrained")
    x = range(len(labels))
    bars = ax.bar(x, values, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Rate (1.0 = all scenarios passed)")
    ax.set_title("Agent eval harness — bundled scenarios (deterministic, no LLM API)")
    for i, b in enumerate(bars):
        ax.text(
            b.get_x() + b.get_width() / 2.0,
            b.get_height() + 0.02,
            f"{values[i]:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    n = report_dict.get("scenarios_run", 0)
    ax.axhline(1.0, color="#666", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.text(
        0.02,
        0.02,
        f"scenarios_run={n} — CI baseline: examples/baselines/agent_eval_baseline.json",
        transform=ax.transAxes,
        fontsize=8,
        color="#333",
        verticalalignment="bottom",
    )
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def _figure_safety_usecase_claims(out: Path, claims_path: Path) -> None:
    """Thin wrapper: illustrative P2 fixture (keeps old filename)."""
    figure_claims_rich(out, claims_path, title_suffix="P2 fixture")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write docs/preprint/figures/*.png + benchmark_bundle.json")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: repo docs/preprint/figures)",
    )
    parser.add_argument(
        "--mission-outputs",
        type=Path,
        default=None,
        help="Mission outputs/ for case-study figures (default: data/missions/4f6715a65f4c/outputs if present)",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = args.out_dir or (repo_root / "docs" / "preprint" / "figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    case_out = args.mission_outputs
    if case_out is None:
        default_m = repo_root / "data" / "missions" / "4f6715a65f4c" / "outputs"
        if default_m.is_dir() and (default_m / "run_ledger.json").is_file():
            case_out = default_m

    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td))
    payload = scorecard_to_stable_dict(report)
    (out_dir / "agent_eval_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    bundle = build_benchmark_bundle(
        repo_root=repo_root,
        case_study_outputs=case_out,
        agent_eval_report_payload=payload,
    )
    (out_dir / "benchmark_bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "benchmark_table.md").write_text(
        benchmark_bundle_to_markdown_table(bundle),
        encoding="utf-8",
    )

    _legacy_figure_agent_eval_scorecard(out_dir / "fig_agent_eval_scorecard.png", payload)
    figure_agent_eval_per_scenario(out_dir / "fig_agent_eval_per_scenario.png", payload)

    sc = payload.get("scorecard") or {}
    axes = sc.get("axes") if isinstance(sc, dict) else None
    if isinstance(axes, dict) and axes:
        try:
            figure_scorecard_axes(out_dir / "fig_agent_eval_axes.png", payload)
        except (ValueError, ImportError) as e:
            print(f"skip fig_agent_eval_axes: {e}", flush=True)

    try:
        figure_scorecard_radar(out_dir / "fig_agent_eval_radar.png", payload)
    except (ValueError, ImportError) as e:
        print(f"skip fig_agent_eval_radar: {e}", flush=True)

    claims_fixture = repo_root / "examples" / "safety_usecase" / "outputs" / "evidence" / "claims.json"
    _figure_safety_usecase_claims(out_dir / "fig_safety_usecase_claim_types.png", claims_fixture)

    if case_out and (case_out / "evidence" / "claims.json").is_file():
        try:
            figure_claims_rich(
                out_dir / "fig_case_study_claim_types.png",
                case_out / "evidence" / "claims.json",
                title_suffix="reference mission",
            )
        except (OSError, ValueError, ImportError) as e:
            print(f"skip fig_case_study_claim_types: {e}", flush=True)

    ledger = case_out / "run_ledger.json" if case_out else None
    if ledger and ledger.is_file():
        try:
            figure_ledger_timeline(out_dir / "fig_case_study_phase_durations.png", ledger)
        except (OSError, ValueError, ImportError) as e:
            print(f"skip fig_case_study_phase_durations: {e}", flush=True)

    print(f"Wrote figures, agent_eval_report.json, benchmark_bundle.json, benchmark_table.md under {out_dir}")


if __name__ == "__main__":
    main()
