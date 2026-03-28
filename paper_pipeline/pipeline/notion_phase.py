"""Notion sync step."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path

from paper_pipeline.constants import ExitCode
from paper_pipeline.events import emit_event
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.notion_sync import sync_sections
from paper_pipeline.state import RunState

logger = logging.getLogger(__name__)


def run_notion_phase(
    mission: Mission,
    out: Path,
    code_dir: Path,
    written: list[tuple[str, Path]],
    state: RunState,
    state_path: Path,
    plog: PipelineLogger,
    *,
    event_sink: Callable[[dict], None] | None,
    manifest: PipelineManifest | None,
) -> int:
    """Returns process exit code (0 or NOTION_AUTH_ERROR)."""

    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    if mission.enable_notion and mission.notion_page_id and notion_token:
        if state.already_done("step:notion"):
            plog.step_skip("step:notion", reason="already completed in previous run")
            if manifest:
                manifest.upsert_phase("notion_sync", "skipped")
                manifest.write(out)
            return 0

        if manifest:
            manifest.upsert_phase("notion_sync", "running")

        log_path = out / "notion_sync.log"
        plog.step_start("step:notion")
        ns_result = sync_sections(
            notion_token,
            mission.notion_page_id,
            [
                (p.stem if p.parent != code_dir else f"code/{p.name}", p)
                for _, p in written
                if p.exists()
            ],
            log_path,
        )
        if not ns_result.ok:
            logger.error("Notion sync had failures: %s", ns_result.errors)
            plog.step_error(
                "step:notion",
                error="notion_sync_failed",
                detail="; ".join(ns_result.errors),
            )
            state.errors.append({"step": "notion", "detail": "; ".join(ns_result.errors)})
            state.save(state_path)
            emit_event(
                out,
                "notion_sync_fail",
                {"errors": ns_result.errors},
                sink=event_sink,
            )
            if manifest:
                manifest.upsert_phase(
                    "notion_sync",
                    "failed",
                    error="; ".join(ns_result.errors),
                )
                manifest.write(out)
            return ExitCode.NOTION_AUTH_ERROR

        plog.step_ok("step:notion")
        emit_event(out, "notion_sync_ok", {}, sink=event_sink)
        state.mark_done("step:notion")
        state.save(state_path)
        if manifest:
            manifest.upsert_phase("notion_sync", "done")
            manifest.write(out)
        return 0

    if mission.enable_notion:
        log_path = out / "notion_sync.log"
        log_path.write_text(
            "Notion sync skipped: set NOTION_TOKEN and notion_page_id\n",
            encoding="utf-8",
        )
    else:
        (out / "notion_sync.log").write_text(
            "Notion sync disabled (enable_notion: false in mission).\n",
            encoding="utf-8",
        )

    if manifest:
        manifest.upsert_phase("notion_sync", "skipped")
        manifest.write(out)

    return 0
