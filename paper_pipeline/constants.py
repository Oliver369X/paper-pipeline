"""Exit codes and tunables shared across CLIs."""

from __future__ import annotations


class ExitCode:
    """Process exit codes for `paper-pipeline` and related tools.

    Meta-loop (`run_meta_loop`) keeps its own convention: 0=CONTINUE, 1=STOP/limit/error,
    2=empty cursor_turn — see docs/OUTPUTS_REFERENCE.md and README.
    """

    OK = 0
    ERROR = 1
    MISSION_NOT_FOUND = 2
    PERPLEXITY_AUTH_ERROR = 3
    PERPLEXITY_RATE_LIMIT = 4
    CURSOR_CLI_NOT_FOUND = 5
    CURSOR_CLI_AUTH_ERROR = 6
    NOTION_AUTH_ERROR = 7
    LOOP_STALLED = 8


# Optional: set via env `CURSOR_AGENT_VERSION_EXPECTED` to warn in run.log when mismatched.
CURSOR_AGENT_VERSION_EXPECTED_ENV = "CURSOR_AGENT_VERSION_EXPECTED"
