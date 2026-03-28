"""CLI entry for paper-parallel."""

from __future__ import annotations

import subprocess
import sys

from paper_pipeline import parallel_cli


def test_parallel_cli_module_has_main() -> None:
    assert callable(parallel_cli.main)


def test_parallel_cli_help_exits_zero() -> None:
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "from paper_pipeline.parallel_cli import main; import sys; "
            "sys.argv=['paper-parallel','--help']; main()",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0
    assert "triage" in (r.stdout + r.stderr)
