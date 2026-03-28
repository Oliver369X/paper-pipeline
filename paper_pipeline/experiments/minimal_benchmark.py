"""Built-in toy benchmark: numpy-only train/test accuracy (no network, no sklearn).

Writes ``outputs/metrics.json`` compatible with :class:`~paper_pipeline.evidence.metrics_model.MetricsBundle`.
If numpy is missing, writes a skipped bundle (install ``paper-pipeline[experiments]``).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def run_minimal_benchmark(output_dir: Path) -> dict[str, Any]:
    """Run a deterministic linear split on synthetic data; return the written payload."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "metrics.json"
    t0 = time.perf_counter()

    try:
        import numpy as np
    except ImportError:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "exit_code": 0,
            "main": None,
            "math_checks": "UNKNOWN",
            "experiment_runner": {
                "status": "skipped",
                "reason": "numpy not installed; pip install paper-pipeline[experiments] or pip install numpy",
            },
        }
        metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.warning("experiment_runner: numpy missing; wrote skipped metrics.json")
        return payload

    rng = np.random.default_rng(42)
    n = 500
    x = rng.standard_normal((n, 4))
    y = ((x[:, 0] + x[:, 1] * 0.5) > 0).astype(np.int64)
    split = int(n * 0.75)
    x_tr, x_te = x[:split], x[split:]
    y_tr, y_te = y[:split], y[split:]

    maj = int(y_tr.mean() >= 0.5)
    baseline_acc = float(np.mean(y_te == maj))

    xb_tr = np.c_[np.ones(len(x_tr)), x_tr]
    w, *_ = np.linalg.lstsq(xb_tr, y_tr.astype(np.float64), rcond=None)
    pred = (np.c_[np.ones(len(x_te)), x_te] @ w) >= 0.5
    main_acc = float(np.mean(pred == y_te))

    elapsed = time.perf_counter() - t0
    payload = {
        "schema_version": 1,
        "exit_code": 0,
        "main": main_acc,
        "baseline": baseline_acc,
        "coverage": None,
        "math_checks": "PASS",
        "seed": 42,
        "n_runs": 1,
        "runtime_sec": round(elapsed, 4),
        "experiment_runner": {
            "status": "ok",
            "name": "numpy_linear_synthetic",
            "metric_name": "accuracy",
            "higher_is_better": True,
            "notes": "Built-in toy benchmark (synthetic data). Not a published dataset.",
        },
    }
    metrics_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info(
        "experiment_runner: metrics.json main=%.4f baseline=%.4f runtime_sec=%s",
        main_acc,
        baseline_acc,
        payload["runtime_sec"],
    )
    return payload


def write_experiment_error_metrics(output_dir: Path, detail: str) -> None:
    """Persist a failure bundle so triage can still see ``experiment_runner.status``."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    p = output_dir / "metrics.json"
    payload = {
        "schema_version": 1,
        "exit_code": 1,
        "main": None,
        "math_checks": "UNKNOWN",
        "anomaly_detected": True,
        "experiment_runner": {"status": "error", "detail": detail[:4000]},
    }
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
