"""CLI: python -m paper_pipeline.agent_eval [--out PATH] [--scenarios-dir DIR] [--check-baseline PATH]."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from .baseline_compare import compare_report_to_baseline, load_baseline
from .eval_metrics import scorecard_to_stable_dict
from .eval_runner import run_all, scenarios_dir_default


def main() -> None:
    parser = argparse.ArgumentParser(description="Run agent eval scenarios (deterministic).")
    parser.add_argument(
        "--scenarios-dir",
        type=Path,
        default=None,
        help="Directory with *.json scenarios (default: bundled eval_scenarios).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write full JSON report to this file (default: stdout unless --check-baseline only).",
    )
    parser.add_argument(
        "--check-baseline",
        type=Path,
        metavar="BASELINE_JSON",
        default=None,
        help="After running scenarios, compare the scorecard to this baseline file; exit 1 on mismatch.",
    )
    args = parser.parse_args()

    sdir = args.scenarios_dir or scenarios_dir_default()
    with tempfile.TemporaryDirectory() as td:
        allowed = Path(td)
        report = run_all(allowed, scenarios_directory=sdir)

    if args.check_baseline is not None:
        baseline = load_baseline(args.check_baseline)
        errors = compare_report_to_baseline(report, baseline)
        if errors:
            for line in errors:
                print(line, file=sys.stderr)
            sys.exit(1)
        print("agent_eval: baseline check passed", file=sys.stderr)

    payload = scorecard_to_stable_dict(report)
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    elif args.check_baseline is None:
        print(text, end="")


if __name__ == "__main__":
    main()
