"""JSONL structured logging for pipeline runs (`outputs/run.log`)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import UTC, datetime
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

OnEvent = Callable[[dict], None]


class PipelineLogger:
    """Append one JSON object per line to `output_dir/run.log`."""

    RUN_LOG = "run.log"

    def __init__(
        self,
        output_dir: Path,
        *,
        on_event: OnEvent | None = None,
    ) -> None:
        self.log_path = output_dir / self.RUN_LOG
        self.output_dir = output_dir
        self._start_times: dict[str, float] = {}
        self._on_event = on_event
        self._enabled = os.environ.get("PAPER_PIPELINE_DISABLE_RUN_LOG", "").lower() not in (
            "1",
            "true",
            "yes",
        )

    def _write(
        self,
        record: dict,
        *,
        level: str = "info",
        module: str = "paper_pipeline.logger",
    ) -> None:
        record["ts"] = datetime.now(UTC).isoformat()
        record["level"] = level
        record["module"] = module
        if self._on_event is not None:
            try:
                self._on_event(dict(record))
            except Exception:
                logger.exception("PipelineLogger on_event failed")
        if not self._enabled:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line)

    def step_start(self, step: str, **kwargs) -> None:
        self._start_times[step] = time.monotonic()
        self._write(
            {"event": "step_start", "step": step, **kwargs},
            level="info",
            module="paper_pipeline.logger",
        )

    def step_ok(self, step: str, **kwargs) -> None:
        duration = round(time.monotonic() - self._start_times.get(step, time.monotonic()), 2)
        self._write(
            {"event": "step_ok", "step": step, "duration_s": duration, **kwargs},
            level="info",
            module="paper_pipeline.logger",
        )

    def step_skip(self, step: str, reason: str, **kwargs) -> None:
        self._write(
            {"event": "step_skip", "step": step, "reason": reason, **kwargs},
            level="warning",
            module="paper_pipeline.logger",
        )

    def step_error(
        self,
        step: str,
        error: str,
        *,
        exit_code: int | None = None,
        **kwargs,
    ) -> None:
        duration = round(time.monotonic() - self._start_times.get(step, time.monotonic()), 2)
        rec: dict = {
            "event": "step_error",
            "step": step,
            "error": error,
            "duration_s": duration,
            **kwargs,
        }
        if exit_code is not None:
            rec["exit_code"] = exit_code
        self._write(rec, level="error", module="paper_pipeline.logger")

    def draft_snapshot(self, draft_path: Path) -> str | None:
        """Record hash of draft; returns short hash or None if missing."""
        if not draft_path.is_file():
            self._write(
                {"event": "draft_snapshot", "hash": None, "chars": 0},
                level="info",
                module="paper_pipeline.logger",
            )
            return None
        content = draft_path.read_text(encoding="utf-8")
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
        self._write(
            {"event": "draft_snapshot", "hash": h, "chars": len(content)},
            level="info",
            module="paper_pipeline.logger",
        )
        return h

    def cursor_version_line(self, *, agent_bin: str, version_text: str, mismatch: bool) -> None:
        self._write(
            {
                "event": "cursor_version",
                "agent_bin": agent_bin,
                "version": version_text[:500],
                "mismatch_expected": mismatch,
            },
            level="info",
            module="paper_pipeline.logger",
        )

    def cursor_cli_subprocess_done(
        self,
        *,
        cwd: str,
        prompt_chars: int,
        duration_s: float,
        exit_code: int | None = None,
        timed_out: bool = False,
        dry_run: bool = False,
        error: str | None = None,
        attempt_index: int | None = None,
        attempts_total: int | None = None,
    ) -> None:
        """Una línea por invocación real o dry-run del Cursor CLI (auditoría / métricas)."""

        rec: dict = {
            "event": "cursor_cli_subprocess_done",
            "cwd": cwd,
            "prompt_chars": prompt_chars,
            "duration_s": round(duration_s, 3),
            "exit_code": exit_code,
            "timed_out": timed_out,
            "dry_run": dry_run,
        }
        if attempt_index is not None:
            rec["attempt_index"] = attempt_index
        if attempts_total is not None:
            rec["attempts_total"] = attempts_total
        if error:
            rec["error"] = error[:2000]
        ok = dry_run or (not timed_out and not error and exit_code == 0)
        level = "info" if ok else ("warning" if timed_out or exit_code not in (0, None) else "error")
        self._write(rec, level=level, module="paper_pipeline.logger")
