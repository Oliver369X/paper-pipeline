"""CLI: `paper-cursor-agent` — Cursor agent via SDK (default) or CLI fallback."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paper_pipeline.cursor_cli_runner import run_cursor_cli
from paper_pipeline.env import load_dotenv_if_available
from paper_pipeline.mission import load_mission


def main() -> None:
    load_dotenv_if_available()
    parser = argparse.ArgumentParser(
        description="Run Cursor CLI (agent -p --force) with prompts from outputs/ or a file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory for outputs, logs, and cursor_turn.md (default: outputs)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=None,
        help="Working directory for the agent (default: parent of --mission, or current directory)",
    )
    parser.add_argument(
        "--mission",
        type=Path,
        default=None,
        help="Optional mission.md to load topic/venue for the prompt",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Optional file to use as full prompt instead of auto-building from outputs/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intent and write a stub log; do not run agent",
    )
    args = parser.parse_args()

    out = args.output_dir.resolve()
    mission = None
    cwd: Path
    if args.mission is not None and args.mission.is_file():
        mission = load_mission(args.mission)
        cwd = args.cwd.resolve() if args.cwd else args.mission.resolve().parent
    else:
        cwd = args.cwd.resolve() if args.cwd else Path.cwd()

    pf = args.prompt_file.resolve() if args.prompt_file else None

    code = run_cursor_cli(
        cwd=cwd,
        output_dir=out,
        mission=mission,
        prompt_file=pf,
        dry_run=args.dry_run,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
