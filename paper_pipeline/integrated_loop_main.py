"""CLI: `paper-loop` — bucle reactivo (directivas + meta-loop)."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.agent.safety import SafetyContext, SafetyController
from paper_pipeline.agent.goal_selection import update_goal_selection_artifacts
from paper_pipeline.agent.objective_state import update_objective_artifacts
from paper_pipeline.agent.research_memory import append_research_memory
from paper_pipeline.agent.safety_trace import append_safety_trace
from paper_pipeline.constants import ExitCode
from paper_pipeline.integrated_loop import DEFAULT_GOAL, run_integrated_cycle
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.mission import load_mission
from paper_pipeline.validation.loop_stall_detector import is_stalled


def _loop_dir(out: Path) -> Path:
    d = out / "loop"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_stop_decision(
    out: Path,
    *,
    cycle: int,
    reasons: list[str],
    consecutive_stalls: int,
) -> Path:
    p = _loop_dir(out) / "stop_decision.json"
    payload = {
        "status": "stopped",
        "reasons": reasons,
        "cycle": cycle,
        "consecutive_stalls": consecutive_stalls,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def main() -> None:
    from paper_pipeline.env import load_dotenv_if_available

    load_dotenv_if_available()
    parser = argparse.ArgumentParser(
        description=(
            "Bucle reactivo: ejecuta @PERPLEXITY / @NOTION / @CURSOR en "
            "cursor_turn.md y next_instruction.md, luego paper-meta-loop (Perplexity revisor)."
        ),
    )
    parser.add_argument(
        "mission",
        nargs="?",
        default="mission.md",
        type=Path,
        help="Archivo de misión (default: ./mission.md)",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=1,
        help="Repetir ciclo hasta STOP de meta o este límite (default: 1)",
    )
    parser.add_argument(
        "--no-meta",
        action="store_true",
        help="Solo ejecutar directivas, sin meta-loop",
    )
    parser.add_argument("--goal", type=str, default=DEFAULT_GOAL)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Listar directivas sin llamar APIs",
    )
    args = parser.parse_args()
    path = args.mission.resolve()
    if not path.is_file():
        print(f"No se encuentra la misión: {path}", file=sys.stderr)
        sys.exit(ExitCode.MISSION_NOT_FOUND)

    mission = load_mission(path)
    out = Path(args.output_dir or mission.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    plog = PipelineLogger(out)

    loop_state_path = _loop_dir(out) / "loop_state.json"
    last = 0
    for cycle in range(1, args.max_cycles + 1):
        state_before: dict = {}
        if loop_state_path.is_file():
            try:
                state_before = json.loads(loop_state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                state_before = {}
        prev_draft = str(state_before.get("last_draft_text") or "")

        last = run_integrated_cycle(
            path,
            output_dir=args.output_dir,
            goal=args.goal,
            run_meta=not args.no_meta,
            dry_run=args.dry_run,
        )
        if last != 0 and last != 1 and last != 2:
            sys.exit(last)

        draft_path = out / "draft_paper.md"
        new_text = draft_path.read_text(encoding="utf-8") if draft_path.is_file() else ""
        full_hash = hashlib.sha256(new_text.encode("utf-8")).hexdigest()
        cap = 200_000

        stall_detect = os.environ.get("LOOP_STALL_DETECT", "").lower() in ("1", "true", "yes")
        if stall_detect:
            max_streak = int(
                os.environ.get(
                    "LOOP_STALL_MAX_CONSECUTIVE",
                    os.environ.get("LOOP_STALL_CONSECUTIVE", "2"),
                ),
            )
            min_delta = int(os.environ.get("LOOP_MIN_DELTA_CHARS", "20"))
            consecutive = int(state_before.get("consecutive_stalls", 0) or 0)
            if prev_draft and is_stalled(prev_draft, new_text, min_delta_chars=min_delta):
                consecutive += 1
            else:
                consecutive = 0

            state_payload = {
                "last_draft_sha256": full_hash,
                "last_draft_chars": len(new_text),
                "consecutive_stalls": consecutive,
                "last_draft_text": new_text[:cap],
                "cycle": cycle,
                "updated_at": datetime.now(UTC).isoformat(),
            }
            loop_state_path.write_text(
                json.dumps(state_payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            if consecutive >= max_streak:
                logging.getLogger(__name__).warning(
                    "loop_stalled (consecutive=%s, cycle=%s)",
                    consecutive,
                    cycle,
                )
                _write_stop_decision(
                    out,
                    cycle=cycle,
                    reasons=["draft_stalled_or_minimal_delta"],
                    consecutive_stalls=consecutive,
                )
                safety_ctx = SafetyContext(
                    candidate_action="loop_iteration",
                    loop_stop_reasons=["draft_stalled_or_minimal_delta"],
                    source_artifacts=["loop/stop_decision.json", "loop/loop_state.json"],
                )
                append_safety_trace(out, safety_ctx, SafetyController().evaluate(safety_ctx))
                update_objective_artifacts(out, candidate_action_family="loop_stop")
                append_research_memory(
                    out,
                    kind="loop_stop",
                    summary="Loop detenido por stall del borrador",
                    source_artifacts=["loop/stop_decision.json", "loop/loop_state.json"],
                    payload={
                        "status": "stopped",
                        "reasons": ["draft_stalled_or_minimal_delta"],
                        "cycle": cycle,
                        "consecutive_stalls": consecutive,
                    },
                    tags=["loop", "stall"],
                    confidence=0.9,
                )
                update_goal_selection_artifacts(out)
                plog.step_error(
                    "paper_loop",
                    error="loop_stop",
                    detail=f"consecutive_stalls={consecutive},cycle={cycle}",
                    loop_stop=True,
                )
                sys.exit(ExitCode.LOOP_STALLED)
        else:
            loop_state_path.write_text(
                json.dumps(
                    {
                        "last_draft_sha256": full_hash,
                        "last_draft_chars": len(new_text),
                        "consecutive_stalls": 0,
                        "last_draft_text": new_text[:cap],
                        "cycle": cycle,
                        "updated_at": datetime.now(UTC).isoformat(),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

        if last == 1:
            break

    sys.exit(0 if last in (0, 1, 2) else last)


if __name__ == "__main__":
    main()
