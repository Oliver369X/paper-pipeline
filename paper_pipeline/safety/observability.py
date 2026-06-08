"""Observability and tracing for AI safety evaluations.

Provides comprehensive logging, tracing, and monitoring
for safety evaluations with full traceability.
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TraceLevel(str, Enum):
    """Trace levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SpanStatus(str, Enum):
    """Span status."""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TraceSpan:
    """A single trace span."""

    span_id: str
    name: str
    trace_id: str
    parent_id: str | None = None
    start_time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    end_time: str | None = None
    duration_ms: float = 0.0
    status: SpanStatus = SpanStatus.OK
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": datetime.now(UTC).isoformat(),
            "attributes": attributes or {},
        })

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span."""
        self.attributes[key] = value

    def set_status(self, status: SpanStatus, message: str = "") -> None:
        """Set span status."""
        self.status = status
        if message:
            self.attributes["status_message"] = message

    def finish(self) -> None:
        """Finish the span."""
        self.end_time = datetime.now(UTC).isoformat()
        if self.start_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_ms = (end - start).total_seconds() * 1000

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "name": self.name,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "attributes": self.attributes,
            "events": self.events,
        }


@dataclass
class Trace:
    """A complete trace of a safety evaluation."""

    trace_id: str
    name: str
    start_time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    end_time: str | None = None
    spans: list[TraceSpan] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def create_span(
        self,
        name: str,
        parent_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> TraceSpan:
        """Create a new span in the trace."""
        span_id = f"{self.trace_id}_span_{len(self.spans)}"
        span = TraceSpan(
            span_id=span_id,
            name=name,
            trace_id=self.trace_id,
            parent_id=parent_id,
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def finish(self) -> None:
        """Finish the trace."""
        self.end_time = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "attributes": self.attributes,
            "spans": [s.to_dict() for s in self.spans],
        }

    def get_summary(self) -> dict[str, Any]:
        """Get trace summary."""
        total_spans = len(self.spans)
        error_spans = sum(1 for s in self.spans if s.status == SpanStatus.ERROR)
        total_duration = sum(s.duration_ms for s in self.spans)

        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "total_spans": total_spans,
            "error_spans": error_spans,
            "total_duration_ms": total_duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


class SafetyTracer:
    """Tracer for safety evaluations."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("outputs/safety/traces")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.traces: list[Trace] = []
        self._current_trace: Trace | None = None
        self._span_stack: list[TraceSpan] = []

    def start_trace(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Trace:
        """Start a new trace."""
        trace_id = f"trace_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{len(self.traces)}"
        trace = Trace(
            trace_id=trace_id,
            name=name,
            attributes=attributes or {},
        )
        self.traces.append(trace)
        self._current_trace = trace
        logger.info("Started trace: %s", trace_id)
        return trace

    @contextmanager
    def span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ):
        """Context manager for creating spans."""
        if not self._current_trace:
            raise RuntimeError("No active trace. Call start_trace() first.")

        parent_id = self._span_stack[-1].span_id if self._span_stack else None
        span = self._current_trace.create_span(name, parent_id, attributes)
        self._span_stack.append(span)

        try:
            yield span
        except Exception as exc:
            span.set_status(SpanStatus.ERROR, str(exc))
            span.add_event("exception", {"type": type(exc).__name__, "message": str(exc)})
            raise
        finally:
            span.finish()
            self._span_stack.pop()

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Add event to current span."""
        if self._span_stack:
            self._span_stack[-1].add_event(name, attributes)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set attribute on current span."""
        if self._span_stack:
            self._span_stack[-1].attributes[key] = value

    def finish_trace(self) -> None:
        """Finish current trace."""
        if self._current_trace:
            self._current_trace.finish()
            logger.info("Finished trace: %s", self._current_trace.trace_id)
            self._current_trace = None

    def save_trace(self, trace: Trace) -> Path:
        """Save trace to file."""
        output_path = self.output_dir / f"{trace.trace_id}.json"
        output_path.write_text(
            json.dumps(trace.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Trace saved to %s", output_path)
        return output_path

    def save_all_traces(self) -> list[Path]:
        """Save all traces."""
        paths = []
        for trace in self.traces:
            path = self.save_trace(trace)
            paths.append(path)
        return paths

    def get_trace_report(self) -> dict[str, Any]:
        """Generate trace report."""
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_traces": len(self.traces),
            "traces": [t.get_summary() for t in self.traces],
        }


class SafetyMetricsCollector:
    """Collects and aggregates safety metrics over time."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("outputs/safety/metrics_history")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_history: list[dict[str, Any]] = []

    def record_metrics(
        self,
        session_id: str,
        metrics: dict[str, Any],
    ) -> None:
        """Record metrics for a session."""
        entry = {
            "session_id": session_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": metrics,
        }
        self.metrics_history.append(entry)
        logger.info("Recorded metrics for session %s", session_id)

    def get_trend(
        self,
        metric_name: str,
        last_n: int = 10,
    ) -> list[float]:
        """Get trend for a specific metric."""
        values = []
        for entry in self.metrics_history[-last_n:]:
            if metric_name in entry.get("metrics", {}):
                values.append(entry["metrics"][metric_name])
        return values

    def save_history(self) -> Path:
        """Save metrics history."""
        output_path = self.output_dir / "metrics_history.json"
        output_path.write_text(
            json.dumps(self.metrics_history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Metrics history saved to %s", output_path)
        return output_path

    def load_history(self) -> None:
        """Load metrics history from file."""
        input_path = self.output_dir / "metrics_history.json"
        if input_path.exists():
            self.metrics_history = json.loads(input_path.read_text(encoding="utf-8"))
            logger.info("Loaded %d metric entries", len(self.metrics_history))


@dataclass
class ObservabilityReport:
    """Comprehensive observability report."""

    session_id: str
    timestamp: str
    traces: list[dict[str, Any]] = field(default_factory=list)
    metrics_history: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "traces": self.traces,
            "metrics_history": self.metrics_history,
            "summary": self.summary,
        }

    def save(self, output_path: Path) -> None:
        """Save observability report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Observability report saved to %s", output_path)


def create_tracer(output_dir: Path | None = None) -> SafetyTracer:
    """Create a safety tracer instance."""
    return SafetyTracer(output_dir=output_dir)


def create_metrics_collector(output_dir: Path | None = None) -> SafetyMetricsCollector:
    """Create a metrics collector instance."""
    return SafetyMetricsCollector(output_dir=output_dir)
