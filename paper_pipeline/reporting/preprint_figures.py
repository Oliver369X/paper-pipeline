"""Rich publication figures for the preprint bundle (matplotlib)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _plt():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import rcParams

        return plt, rcParams
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            'matplotlib required: pip install -e ".[figures]"',
        ) from exc


def _default_rc() -> dict[str, Any]:
    return {
        "font.family": "serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.grid": True,
        "grid.alpha": 0.25,
    }


def figure_agent_eval_per_scenario(out: Path, report_dict: dict[str, Any]) -> None:
    """One bar per scenario: pass=1 / fail=0 (deterministic harness)."""
    plt, rcParams = _plt()
    rcParams.update(_default_rc())
    results = report_dict.get("results") or []
    if not isinstance(results, list) or not results:
        raise ValueError("report_dict has no results")

    labels: list[str] = []
    vals: list[float] = []
    colors: list[str] = []
    for r in results:
        if not isinstance(r, dict):
            continue
        sid = str(r.get("scenario_id", "?"))
        short = sid if len(sid) <= 26 else sid[:23] + "…"
        labels.append(short)
        passed = bool(r.get("passed"))
        vals.append(1.0 if passed else 0.0)
        colors.append("#1b5e20" if passed else "#b71c1c")

    fig_h = max(4.0, min(10.0, 0.35 * len(labels)))
    fig, ax = plt.subplots(figsize=(7.5, fig_h), layout="constrained")
    y = range(len(labels))
    ax.barh(list(y), vals, color=colors, height=0.7, edgecolor="white", linewidth=0.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(-0.05, 1.15)
    ax.set_xlabel("Pass (1) / fail (0)")
    ax.set_title("Agent eval — per-scenario outcomes (deterministic, no LLM API)")
    ax.axvline(1.0, color="#666", linestyle="--", linewidth=0.6, alpha=0.5)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_scorecard_axes(out: Path, report_dict: dict[str, Any]) -> None:
    """Stacked pass/fail counts per governance axis (if present in scorecard)."""
    plt, rcParams = _plt()
    rcParams.update(_default_rc())
    sc = report_dict.get("scorecard") or {}
    axes = sc.get("axes") if isinstance(sc, dict) else None
    if not isinstance(axes, dict) or not axes:
        raise ValueError("scorecard.axes missing or empty")

    names = sorted(axes.keys())
    pass_c = [int(axes[k].get("pass", 0)) for k in names]
    fail_c = [int(axes[k].get("fail", 0)) for k in names]

    fig, ax = plt.subplots(figsize=(6.5, 3.8), layout="constrained")
    x = range(len(names))
    ax.bar(x, pass_c, label="pass", color="#1565c0", edgecolor="white", linewidth=0.5)
    ax.bar(x, fail_c, bottom=pass_c, label="fail", color="#c62828", edgecolor="white", linewidth=0.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names, rotation=18, ha="right")
    ax.set_ylabel("Scenario count")
    ax.set_title("Governance axes — pass vs fail (bundled scenarios)")
    ax.legend(loc="upper right")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_ledger_timeline(out: Path, ledger_path: Path) -> None:
    """Horizontal bars: phase duration (seconds) from run_ledger.json."""
    plt, rcParams = _plt()
    rcParams.update(_default_rc())
    if not ledger_path.is_file():
        raise FileNotFoundError(ledger_path)
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    from paper_pipeline.reporting.benchmark_bundle import ledger_phase_durations_seconds

    if not isinstance(ledger, dict):
        raise ValueError("invalid ledger")
    rows = ledger_phase_durations_seconds(ledger)
    if not rows:
        raise ValueError("no phase durations")

    names = [r["phase"] for r in rows]
    secs = [float(r["seconds"]) for r in rows]
    palette = ["#0d47a1", "#1565c0", "#1976d2", "#1e88e5", "#2196f3", "#42a5f5", "#64b5f6", "#90caf9"]
    colors = [palette[i % len(palette)] for i in range(len(names))]

    fig_h = max(3.8, min(0.42 * len(names), 12.0))
    fig, ax = plt.subplots(figsize=(7.2, fig_h), layout="constrained")
    y = range(len(names))
    ax.barh(list(y), secs, color=colors, height=0.65, edgecolor="white", linewidth=0.4)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Seconds (wall time per phase)")
    ax.set_title("Case study mission — phase durations (run_ledger)")
    for i, s in enumerate(secs):
        ax.text(s + max(secs) * 0.01, i, f"{s:.1f}s", va="center", fontsize=8, color="#333")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_claims_rich(out: Path, claims_path: Path, *, title_suffix: str = "") -> None:
    """Stacked-style counts by claim type with clearer palette than single gray barh."""
    plt, rcParams = _plt()
    rcParams.update(_default_rc())
    if not claims_path.is_file():
        raise FileNotFoundError(claims_path)
    data = json.loads(claims_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("claims.json must be a list")
    from collections import Counter

    import matplotlib as mpl

    c = Counter(str(item.get("type", "?")) for item in data)
    labels = list(c.keys())
    vals = [c[k] for k in labels]
    try:
        cmap = mpl.colormaps["tab20c"]
    except (AttributeError, KeyError):
        cmap = mpl.cm.get_cmap("tab20c")
    colors_fwd = [cmap(i / max(len(labels), 1)) for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(6.5, max(3.2, 0.28 * len(labels))), layout="constrained")
    ax.barh(labels[::-1], vals[::-1], color=colors_fwd[::-1])
    ax.set_xlabel("Count")
    ttl = "Heuristic claim candidates by type"
    if title_suffix:
        ttl += f" — {title_suffix}"
    ax.set_title(ttl)
    ax.grid(axis="x", alpha=0.3)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_scorecard_radar(out: Path, report_dict: dict[str, Any]) -> None:
    """Radar-style plot of aggregate rates (scenario, safety, goal) when ≥2 dimensions."""
    plt, rcParams = _plt()
    rcParams.update(_default_rc())
    sc = report_dict.get("scorecard") or {}
    if not isinstance(sc, dict):
        raise ValueError("no scorecard")

    labels: list[str] = []
    vals: list[float] = []
    labels.append("scenario\npass rate")
    vals.append(float(sc.get("scenario_pass_rate", 0.0)))
    sr = sc.get("safety_correct_rate")
    gr = sc.get("goal_selection_correct_rate")
    if sr is not None:
        labels.append("safety\ncorrect")
        vals.append(float(sr))
    if gr is not None:
        labels.append("goal\nselection")
        vals.append(float(gr))

    if len(labels) < 2:
        fig, ax = plt.subplots(figsize=(4.2, 2.8), layout="constrained")
        ax.bar(range(len(labels)), vals, color="#1565c0", edgecolor="white")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("Rate")
        ax.set_title("Agent eval — aggregate rates")
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)
        return

    fig, ax = plt.subplots(figsize=(4.0, 4.0), subplot_kw=dict(polar=True), layout="constrained")
    import math

    n = len(labels)
    angles = [2 * math.pi * i / n for i in range(n)]
    angles += angles[:1]
    vals_plot = vals + vals[:1]
    ax.plot(angles, vals_plot, "o-", color="#0d47a1", linewidth=1.8)
    ax.fill(angles, vals_plot, alpha=0.22, color="#1565c0")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_title("Agent eval — aggregate rates (radar)", y=1.08)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
