"""Console script ``paper-agent-eval-check`` — default baseline path when run from repo root."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    from paper_pipeline.agent_eval.__main__ import main as agent_eval_main

    if len(sys.argv) == 1:
        sys.argv = [
            sys.argv[0],
            "--check-baseline",
            str(Path("examples/baselines/agent_eval_baseline.json")),
        ]
    agent_eval_main()
