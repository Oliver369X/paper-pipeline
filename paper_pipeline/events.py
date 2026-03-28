"""Structured pipeline events (`outputs/pipeline_events.jsonl`) + optional SSE sink."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

OnEvent = Callable[[dict[str, Any]], None]

_PIPELINE_EVENTS = "pipeline_events.jsonl"


def emit_event(
    output_dir: Path,
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    sink: OnEvent | None = None,
) -> None:
    """Append one JSON line to ``outputs/pipeline_events.jsonl`` and optionally forward to *sink*.

    Typical *event_type* values: ``section_start``, ``section_done``, ``draft_assembled``,
    ``notion_sync_ok``, ``notion_sync_fail``, ``loop_cycle``, ``meta_round``, ``triage_result``.
    """

    if os.environ.get("PAPER_PIPELINE_DISABLE_EVENTS", "").lower() in ("1", "true", "yes"):
        return

    rec: dict[str, Any] = {
        "event": event_type,
        "ts": datetime.now(UTC).isoformat(),
    }
    if payload:
        rec.update(payload)

    if sink is not None:
        try:
            sink(dict(rec))
        except Exception:
            pass

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / _PIPELINE_EVENTS
    line = json.dumps(rec, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
