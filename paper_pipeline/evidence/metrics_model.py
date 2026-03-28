"""Versioned metrics bundle (triage input)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class MetricsBundle(BaseModel):
    """``outputs/metrics.json`` with optional schema version."""

    schema_version: int = 1
    exit_code: int = 0
    main: float | None = None
    baseline: float | None = None
    coverage: float | None = Field(default=None, ge=0.0, le=1.0)
    math_checks: Literal["PASS", "FAIL", "UNKNOWN"] = "UNKNOWN"
    anomaly_detected: bool = False
    oom_error: bool = False
    seed: int | None = None
    n_runs: int | None = None
    runtime_sec: float | None = None
    dataset_hash: str | None = None
    code_commit: str | None = None

    model_config = {"extra": "allow"}


def metrics_json_schema() -> dict[str, Any]:
    return MetricsBundle.model_json_schema()
