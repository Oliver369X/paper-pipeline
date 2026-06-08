#!/usr/bin/env python3
"""Emit a Markdown audit table for numbers cited in the preprint (reads JSON from disk; no network)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paper_pipeline.reporting.abstract_audit import run_audit


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: parent of scripts/)",
    )
    p.add_argument(
        "--mission-outputs",
        type=Path,
        default=None,
        help="Mission outputs/ directory (default: data/missions/4f6715a65f4c/outputs)",
    )
    p.add_argument(
        "--claims",
        type=Path,
        default=None,
        help="Optional override path to claims.json",
    )
    args = p.parse_args()
    repo = (args.repo_root or Path(__file__).resolve().parents[1]).resolve()
    mout = args.mission_outputs or (repo / "data" / "missions" / "4f6715a65f4c" / "outputs")
    text = run_audit(repo_root=repo, mission_outputs=mout, claims_path=args.claims)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
