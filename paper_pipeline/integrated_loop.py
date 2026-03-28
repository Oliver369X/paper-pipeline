"""Bucle reactivo real: @PERPLEXITY / @NOTION / @CURSOR en markdown + meta-loop (Perplexity).

Tras cada ciclo, la persistencia de ``loop_state.json``, la detección de estancamiento
(``is_stalled``) y ``outputs/loop/stop_decision.json`` las resuelve el CLI ``paper-loop``
(``integrated_loop_main``) al final de ``run_integrated_cycle``, no dentro de este módulo.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path

from filelock import FileLock, Timeout
from perplexity_webui_scraper import ClientConfig, Perplexity

from paper_pipeline.cursor_cli_runner import run_cursor_cli
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.loop_directives import (
    CursorDirective,
    NotionDirective,
    PerplexityDirective,
    parse_directives,
    strip_directive_blocks,
)
from paper_pipeline.meta_loop import run_meta_loop
from paper_pipeline.mission import Mission, load_mission
from paper_pipeline.notion_sync import sync_sections
from paper_pipeline.orchestrator import rebuild_draft_from_outputs, run_one_perplexity_section

logger = logging.getLogger(__name__)

DEFAULT_GOAL = (
    "Completar el paper pipeline: código bajo outputs/code/ alineado con methodology y experiments."
)


def execute_directives_from_files(
    mission: Mission,
    out: Path,
    mission_dir: Path,
    *,
    dry_run: bool = False,
    pipeline_log: PipelineLogger | None = None,
) -> tuple[int, bool]:
    """Run @ directives from cursor_turn.md then next_instruction.md. Returns (exit_code, draft_rebuilt)."""

    ct = out / "cursor_turn.md"
    ni = out / "next_instruction.md"
    paths = [p for p in (ct, ni) if p.is_file()]
    if not paths:
        return 0, False

    plog = pipeline_log or PipelineLogger(out)

    any_perplexity = False
    segments: list[tuple[Path, str, list]] = []
    for path in paths:
        lock_path = path.with_name(path.name + ".lock")
        try:
            with FileLock(str(lock_path), timeout=10):
                raw = path.read_text(encoding="utf-8")
        except Timeout:
            logger.error("No se pudo adquirir lock para %s (timeout)", path)
            plog.step_error("directives", error="file_lock_timeout", path=str(path))
            return 1, False
        dirs = parse_directives(raw)
        if dirs:
            segments.append((path, raw, dirs))

    if not segments:
        return 0, False

    if dry_run:
        for _path, _raw, dirs in segments:
            logger.info("Dry-run: would execute %s directive(s): %s", len(dirs), dirs)
        return 0, False

    need_client = any(
        isinstance(d, PerplexityDirective) for _p, _r, ds in segments for d in ds
    )
    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    if need_client and not token:
        logger.error("PERPLEXITY_SESSION_TOKEN requerido para @PERPLEXITY")
        plog.step_error("directives", error="perplexity_auth_error", detail="token missing")
        return 1, False

    plog.step_start("directives", count=sum(len(ds) for _p, _r, ds in segments))

    client: Perplexity | None = None
    if need_client:
        client = Perplexity(token, config=ClientConfig())

    try:
        for path, raw, dirs in segments:
            lock_path = path.with_name(path.name + ".lock")
            with FileLock(str(lock_path), timeout=10):
                for d in dirs:
                    if isinstance(d, PerplexityDirective):
                        try:
                            assert client is not None
                            plog.step_start(f"perplexity:{d.section}", source="loop_directive")
                            run_one_perplexity_section(
                                mission,
                                d.section,
                                out,
                                client=client,
                                extra_prompt=d.body,
                            )
                            plog.step_ok(f"perplexity:{d.section}")
                        except KeyError:
                            logger.exception("Sección desconocida: %s", d.section)
                            plog.step_error("perplexity", error="unknown_section", section=d.section)
                            return 1, False
                        any_perplexity = True
                    elif isinstance(d, NotionDirective):
                        plog.step_start("notion")
                        _run_notion_sync(mission, out)
                        plog.step_ok("notion")
                    elif isinstance(d, CursorDirective):
                        plog.step_start("cursor_cli")
                        code = run_cursor_cli(
                            cwd=mission_dir,
                            output_dir=out,
                            mission=mission,
                            prompt=d.body if d.body.strip() else None,
                            dry_run=False,
                            pipeline_log=plog,
                        )
                        if code != 0:
                            plog.step_error("cursor_cli", error="cursor_cli_failed", exit_code=code)
                            return code, any_perplexity
                        plog.step_ok("cursor_cli")
                path.write_text(strip_directive_blocks(raw), encoding="utf-8")
    finally:
        if client is not None:
            client.close()

    if any_perplexity:
        rebuild_draft_from_outputs(out, mission)
        plog.draft_snapshot(out / "draft_paper.md")

    plog.step_ok("directives")
    return 0, True


def _run_notion_sync(mission: Mission, out: Path) -> None:
    notion_token = os.environ.get("NOTION_TOKEN", "").strip()
    if not mission.enable_notion or not mission.notion_page_id or not notion_token:
        logger.warning(
            "@NOTION omitido: enable_notion, notion_page_id o NOTION_TOKEN no disponibles",
        )
        return
    code_dir = out / "code"
    skip = {
        "draft_paper.md",
        "quality_gaps.md",
        "cursor_turn.md",
        "next_instruction.md",
        "meta_loop_log.md",
    }
    pairs: list[tuple[str, Path]] = []
    for p in sorted(out.glob("*.md")):
        if p.name in skip:
            continue
        pairs.append((p.stem, p))
    if (code_dir / "README.md").is_file():
        pairs.append(("code/README.md", code_dir / "README.md"))
    log_path = out / "notion_sync.log"
    result = sync_sections(notion_token, mission.notion_page_id, pairs, log_path)
    if not result.ok:
        logger.warning("Notion sync con errores parciales: %s", result.errors)
    logger.info("Notion sync ejecutado (%s archivos)", len(pairs))


def run_integrated_cycle(
    mission_path: Path,
    *,
    output_dir: Path | None = None,
    goal: str = DEFAULT_GOAL,
    run_meta: bool = True,
    dry_run: bool = False,
    event_sink: Callable[[dict], None] | None = None,
) -> int:
    """Un ciclo: directivas en markdown + opcional meta-loop (Perplexity revisor)."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    mission = load_mission(mission_path)
    out = Path(output_dir or mission.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    mission_dir = mission_path.resolve().parent

    plog = PipelineLogger(out, on_event=event_sink)

    if dry_run:
        execute_directives_from_files(mission, out, mission_dir, dry_run=True)
        return 0

    code, _ = execute_directives_from_files(
        mission,
        out,
        mission_dir,
        dry_run=False,
        pipeline_log=plog,
    )
    if code != 0:
        return code

    if not run_meta:
        return 0

    plog.step_start("meta_loop")
    meta_code = run_meta_loop(out, goal=goal, model=mission.model)
    plog.step_ok("meta_loop", decision_code=meta_code)
    return meta_code
