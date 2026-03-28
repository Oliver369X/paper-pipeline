"""CLI entry: `paper-pipeline` or `python -m paper_pipeline`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from paper_pipeline.env import load_dotenv_if_available
from paper_pipeline.orchestrator import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser (testable without running the pipeline)."""
    parser = argparse.ArgumentParser(description="Run paper research pipeline from mission.md")
    parser.add_argument(
        "mission",
        nargs="?",
        default="mission.md",
        type=Path,
        help="Path to mission file (default: ./mission.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate mission file only; no Perplexity calls",
    )
    parser.add_argument(
        "--v2",
        action="store_true",
        help="Use v2 wrapper (epistemic injection / degradation hooks per mission.md)",
    )
    return parser


def _select_runner(use_v2: bool) -> Callable[..., int]:
    """Return the pipeline entrypoint (v1 or v2) without wrapping or mocking."""
    if use_v2:
        from paper_pipeline.orchestrator_v2 import run_pipeline_v2

        return run_pipeline_v2
    return run_pipeline


def main(argv: list[str] | None = None) -> None:
    load_dotenv_if_available()
    args = build_parser().parse_args(argv)
    path = args.mission.resolve()
    if not path.is_file():
        print(f"Error: mission file not found: {path}", file=sys.stderr)
        sys.exit(2)
    runner = _select_runner(args.v2)
    code = runner(path, dry_run=args.dry_run)
    sys.exit(code)


if __name__ == "__main__":
    main()
