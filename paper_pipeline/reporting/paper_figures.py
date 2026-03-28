"""Figures and English snippets for paper drafts (from ``TriageMetrics`` / ``metrics.json``).

Requires optional dependency: ``pip install matplotlib`` or ``pip install -e ".[figures]"``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_metrics_dict(path: Path) -> dict[str, Any]:
    """Load ``metrics.json``; returns empty dict if missing or invalid."""

    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def sota_claim_paragraph_en(
    *,
    metric_name: str,
    measured: float,
    baseline: float,
    beats_baseline: bool,
    tolerance: float = 0.0,
) -> str:
    """Neutral academic paragraph for a Results subsection (English, third person)."""

    delta = measured - baseline
    rel = (delta / baseline * 100.0) if baseline not in (0.0, -0.0) else float("nan")
    cmp_word = "exceeds" if beats_baseline else "does not exceed"
    lines = [
        f"We report {metric_name} = {measured:.4f} against a stated baseline of {baseline:.4f} "
        f"(absolute difference {delta:+.4f}; relative change {rel:+.2f}% vs. baseline, where defined). "
        f"The observed value {cmp_word} the baseline",
    ]
    if tolerance > 0:
        lines[0] += f" under a replication tolerance of ±{tolerance:.4f}."
    else:
        lines[0] += "."
    lines.append(
        "Interpretation should account for measurement noise, dataset shift, and "
        "whether the baseline is directly comparable (same task, split, and preprocessing)."
    )
    return "\n\n".join(lines)


def figure_main_vs_baseline(
    metrics_path: Path,
    out_path: Path,
    *,
    metric_label: str = "Score",
    title: str | None = None,
    language: str = "en",
) -> None:
    """Bar chart: ``main`` vs ``baseline`` from ``metrics.json`` (300 dpi, serif)."""

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "matplotlib is required for figures. Install with: pip install matplotlib "
            'or pip install -e ".[figures]"',
        ) from exc

    data = load_metrics_dict(metrics_path)
    main = data.get("main")
    baseline = data.get("baseline")
    if main is None:
        raise ValueError(f'"main" missing or null in {metrics_path}')

    labels_en = ("Measured (main)", "Baseline / SOTA ref.")
    labels_es = ("Medida (main)", "Baseline / ref. SOTA")
    labels = labels_es if language.lower().startswith("es") else labels_en

    vals = [float(main)]
    colors = ["#1f4e79"]
    if baseline is not None:
        vals.insert(0, float(baseline))
        colors = ["#8c8c8c", "#1f4e79"]
        bar_labels = [labels[1], labels[0]]
    else:
        bar_labels = [labels[0]]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 11,
            "axes.labelsize": 11,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )
    fig, ax = plt.subplots(figsize=(4.0, 3.2))
    x = range(len(vals))
    ax.bar(x, vals, color=colors, edgecolor="black", linewidth=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(bar_labels, rotation=12, ha="right")
    ax.set_ylabel(metric_label)
    ttl = title or (
        "Main metric vs. baseline"
        if language.lower().startswith("en")
        else "Métrica principal vs. baseline"
    )
    ax.set_title(ttl)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    """CLI: ``paper-report-figures metrics.json -o figure.png``."""

    p = argparse.ArgumentParser(description="Render paper figure from outputs/metrics.json")
    p.add_argument("metrics", type=Path, help="Path to metrics.json")
    p.add_argument("-o", "--output", type=Path, required=True, help="Output .png path")
    p.add_argument(
        "--metric-label",
        default="Score",
        help="Y-axis label (e.g. Accuracy, F1, BLEU)",
    )
    p.add_argument("--title", default=None, help="Figure title")
    p.add_argument("--lang", default="en", choices=("en", "es"), help="Axis language")
    args = p.parse_args(argv)

    try:
        figure_main_vs_baseline(
            args.metrics,
            args.output,
            metric_label=args.metric_label,
            title=args.title,
            language=args.lang,
        )
    except (ValueError, OSError, ImportError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
