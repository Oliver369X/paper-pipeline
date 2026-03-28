"""Tier classification for parallel experiments (Hipervisor de Triaje).

Tier 0 — Crash / invalid: non-zero exit, OOM, coverage < 50%, or missing critical signals.
Tier 1 — Refuted: math checks pass but main metric below SOTA baseline (honest negative result).
Tier 2 — SOTA match: within replication tolerance of baseline.
Tier 3 — Breakthrough: main exceeds baseline + margin, or anomaly flag.

Destructive actions (delete branch, Notion) are **not** performed here — only JSON/Markdown artifacts.

Optional: ``PAPER_PIPELINE_TRIAGE_WEBHOOK_URL`` — HTTPS POST JSON when tier == 3 (breakthrough).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field

from paper_pipeline.evidence.metrics_io import load_and_validate_metrics
from paper_pipeline.evidence.metrics_model import MetricsBundle
from paper_pipeline.agent.research_memory import append_research_memory
from paper_pipeline.mission import Mission

logger = logging.getLogger(__name__)

# Minimum test coverage (fraction 0–1) to avoid Tier 0 for "unmeasured" runs.
_COVERAGE_FLOOR = 0.50

WEBHOOK_ENV = "PAPER_PIPELINE_TRIAGE_WEBHOOK_URL"
WEBHOOK_TIMEOUT_SEC = 15.0


def _append_event_jsonl(triage_dir: Path, event: dict[str, Any]) -> None:
    """Append one NDJSON line for local audit / future Notion sync."""
    line = json.dumps(event, ensure_ascii=False) + "\n"
    p = triage_dir / "events.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(line)


def _post_webhook_breakthrough(url: str, body: dict[str, Any]) -> None:
    """POST JSON; failures are logged and swallowed (never fail the pipeline)."""
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urlopen(req, timeout=WEBHOOK_TIMEOUT_SEC) as resp:
        resp.read(10_000)


def _maybe_notify_notion(
    mission: Mission,
    report: TriageReport,
    metrics: TriageMetrics,
    output_dir: Path,
) -> None:
    """Append to Notion page when NOTION_TOKEN + NOTION_TRIAGE_PAGE_ID are set (tier 3)."""
    if report.tier != 3:
        return
    try:
        from paper_pipeline.notion_telemetry import (
            maybe_append_triage_breakthrough_to_notion,
        )

        maybe_append_triage_breakthrough_to_notion(
            mission,
            tier=report.tier,
            label=report.label,
            reason=report.reason,
            detail=report.detail,
            metrics=metrics.model_dump(),
            output_dir=output_dir,
        )
    except Exception as exc:
        logger.warning("Notion telemetry failed: %s", exc)


def _maybe_notify_webhook(
    mission: Mission,
    report: TriageReport,
    metrics: TriageMetrics,
    output_dir: Path,
) -> None:
    if report.tier != 3:
        return
    url = os.environ.get(WEBHOOK_ENV, "").strip()
    if not url:
        return
    body = {
        "event": "paper_pipeline.triage.breakthrough",
        "tier": report.tier,
        "label": report.label,
        "reason": report.reason,
        "detail": report.detail,
        "topic": mission.topic,
        "paper_target": mission.paper_target,
        "output_dir": str(output_dir.resolve()),
        "metrics": metrics.model_dump(),
        "ts": datetime.now(UTC).isoformat(),
    }
    try:
        _post_webhook_breakthrough(url, body)
        logger.info("Breakthrough webhook delivered to %s", url[:48] + ("…" if len(url) > 48 else ""))
    except (URLError, OSError, TimeoutError, ValueError) as exc:
        logger.warning("Breakthrough webhook failed: %s", exc)


class TriageMetrics(BaseModel):
    """Optional metrics dropped into ``outputs/metrics.json`` by experiments or harness."""

    exit_code: int = 0
    main: float | None = None
    baseline: float | None = None
    coverage: float | None = Field(
        default=None,
        description="Fraction 0–1 of test coverage",
    )
    math_checks: str | None = Field(
        default=None,
        description="PASS or FAIL",
    )
    anomaly_detected: bool = False
    oom_error: bool = False
    notes: str = ""


def metrics_bundle_to_triage_metrics(bundle: MetricsBundle) -> TriageMetrics:
    """Map validated :class:`MetricsBundle` to triage classification input."""
    d = bundle.model_dump()
    mc = bundle.math_checks
    math_str: str | None = None if mc == "UNKNOWN" else mc
    return TriageMetrics(
        exit_code=int(d.get("exit_code", 0)),
        main=d.get("main"),
        baseline=d.get("baseline"),
        coverage=d.get("coverage"),
        math_checks=math_str,
        anomaly_detected=bool(d.get("anomaly_detected", False)),
        oom_error=bool(d.get("oom_error", False)),
        notes=str(d.get("notes") or ""),
    )


@dataclass
class TriageReport:
    tier: int
    label: str
    reason: str
    detail: dict[str, Any]


def load_metrics_file(path: Path) -> TriageMetrics | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read metrics file %s: %s", path, exc)
        return None
    return TriageMetrics.model_validate(data)


def classify_triage(
    metrics: TriageMetrics,
    mission: Mission,
) -> TriageReport:
    """Assign a tier using mission quality gates and recorded metrics."""
    qg = mission.quality_gates
    baseline = metrics.baseline if metrics.baseline is not None else qg.sota_baseline_value
    margin = qg.breakthrough_margin
    tol = qg.replication_tolerance
    higher = qg.higher_is_better

    if metrics.exit_code != 0 or metrics.oom_error:
        return TriageReport(
            0,
            "crash_or_error",
            "Non-zero exit_code or OOM flag",
            {"exit_code": metrics.exit_code, "oom": metrics.oom_error},
        )

    if metrics.coverage is not None and metrics.coverage < _COVERAGE_FLOOR:
        return TriageReport(
            0,
            "low_coverage",
            f"Coverage {metrics.coverage:.2f} below floor {_COVERAGE_FLOOR}",
            {"coverage": metrics.coverage},
        )

    math_ok = (metrics.math_checks or "").upper() == "PASS"

    if metrics.main is None:
        return TriageReport(
            2,
            "insufficient_metrics",
            "No primary metric; classified as neutral match (no breakthrough claim)",
            {},
        )

    if metrics.anomaly_detected:
        return TriageReport(
            3,
            "breakthrough",
            "Anomaly flag set — requires human review",
            {"main": metrics.main, "anomaly": True},
        )

    if higher:
        breakthrough = metrics.main >= baseline + margin
    else:
        breakthrough = metrics.main <= baseline - margin

    if breakthrough:
        return TriageReport(
            3,
            "breakthrough",
            "Main metric crosses breakthrough margin vs baseline",
            {"main": metrics.main, "baseline": baseline, "margin": margin},
        )

    if math_ok and (
        (higher and metrics.main < baseline) or (not higher and metrics.main > baseline)
    ):
        return TriageReport(
            1,
            "refuted",
            "Metric below baseline with math checks PASS (honest negative)",
            {"main": metrics.main, "baseline": baseline},
        )

    if abs(metrics.main - baseline) <= tol:
        return TriageReport(
            2,
            "sota_match",
            "Within replication tolerance of baseline",
            {"main": metrics.main, "baseline": baseline, "tolerance": tol},
        )

    return TriageReport(
        2,
        "inconclusive_or_marginal",
        "Did not match breakthrough, refuted, or tight replication bands",
        {"main": metrics.main, "baseline": baseline},
    )


def write_triage_artifacts(
    output_dir: Path,
    mission: Mission,
    metrics: TriageMetrics,
    report: TriageReport,
    *,
    metrics_validation_errors: list[str] | None = None,
    metrics_relax_mode: bool = False,
    metrics_bundle_strict_errors: list[str] | None = None,
) -> Path:
    """Write ``triage/triage_report.json`` and optional ``triage/FAILURES.md`` for Tier 1."""
    triage_dir = output_dir / "triage"
    triage_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "version": 1,
        "tier": report.tier,
        "label": report.label,
        "reason": report.reason,
        "detail": report.detail,
        "metrics": metrics.model_dump(),
        "quality_gates": mission.quality_gates.model_dump(),
    }
    if metrics_validation_errors:
        payload["metrics_validation_errors"] = metrics_validation_errors
    if metrics_relax_mode:
        payload["metrics_relax_mode"] = True
    if metrics_bundle_strict_errors:
        payload["metrics_bundle_strict_errors"] = metrics_bundle_strict_errors
    report_path = triage_dir / "triage_report.json"
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    event = {
        **payload,
        "topic": mission.topic,
        "output_dir": str(output_dir.resolve()),
        "ts": datetime.now(UTC).isoformat(),
    }
    _append_event_jsonl(triage_dir, event)

    if report.tier == 1:
        failures = triage_dir / "FAILURES.md"
        failures.write_text(
            _format_failures_md(mission, metrics, report),
            encoding="utf-8",
        )

    logger.info(
        "Triage tier %d (%s) — report at %s",
        report.tier,
        report.label,
        report_path,
    )
    append_research_memory(
        output_dir,
        kind="triage",
        summary=f"Triage {report.label} (tier {report.tier})",
        source_artifacts=["triage/triage_report.json"],
        payload=payload,
        tags=["triage", f"tier_{report.tier}", report.label],
        confidence=0.8,
    )
    _maybe_notify_webhook(mission, report, metrics, output_dir)
    _maybe_notify_notion(mission, report, metrics, output_dir)
    return report_path


def _format_failures_md(mission: Mission, metrics: TriageMetrics, report: TriageReport) -> str:
    return (
        "# Experiment autopsy (Tier 1 — refuted)\n\n"
        f"**Topic:** {mission.topic}\n\n"
        f"**Reason:** {report.reason}\n\n"
        f"**Detail:** `{json.dumps(report.detail, ensure_ascii=False)}`\n\n"
        f"**Metrics snapshot:**\n```json\n{json.dumps(metrics.model_dump(), indent=2, ensure_ascii=False)}\n```\n\n"
        "This outcome preserves honest intellectual documentation of a negative result.\n"
    )


def run_triage_for_mission(
    mission: Mission,
    output_dir: Path,
    *,
    metrics_path: Path | None = None,
) -> TriageReport | None:
    """Load metrics, classify, write artifacts. Returns None if no metrics file."""
    mpath = metrics_path or (output_dir / "metrics.json")
    bundle, val_errors = load_and_validate_metrics(mpath)
    if bundle is None and not val_errors:
        logger.info("Hypervisor triage skipped: no metrics at %s", mpath)
        return None
    if val_errors:
        relax = os.environ.get("PAPER_PIPELINE_RELAX_METRICS", "").lower() in (
            "1",
            "true",
            "yes",
        )
        if relax:
            relaxed = load_metrics_file(mpath)
            if relaxed is not None:
                logger.warning(
                    "MetricsBundle validation failed (%d errors); triage uses relaxed "
                    "TriageMetrics parse (PAPER_PIPELINE_RELAX_METRICS). Errors: %s",
                    len(val_errors),
                    val_errors[:3],
                )
                metrics = relaxed
                report = classify_triage(metrics, mission)
                write_triage_artifacts(
                    output_dir,
                    mission,
                    metrics,
                    report,
                    metrics_relax_mode=True,
                    metrics_bundle_strict_errors=val_errors,
                )
                return report
        report = TriageReport(
            0,
            "invalid_metrics",
            "metrics.json failed MetricsBundle validation",
            {"path": str(mpath)},
        )
        metrics = TriageMetrics()
        write_triage_artifacts(
            output_dir,
            mission,
            metrics,
            report,
            metrics_validation_errors=val_errors,
        )
        return report
    assert bundle is not None
    metrics = metrics_bundle_to_triage_metrics(bundle)
    report = classify_triage(metrics, mission)
    write_triage_artifacts(output_dir, mission, metrics, report)
    return report
