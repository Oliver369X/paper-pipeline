"""Basic validation for agent shell commands (parallel worktree batch)."""

from __future__ import annotations

import re
import shlex


_DANGEROUS = re.compile(
    r"(;|\|\||&&|`|\$\(|\$\{|<\s*/dev/|>\s*/dev/|curl\s+\||wget\s+\||rm\s+-rf\s+/|"
    r"mkfs\.|dd\s+if=|:(){ :|:& };|chmod\s+-R\s+777\s+/)",
    re.IGNORECASE,
)


def validate_agent_command(argv: list[str], *, allowed_prefixes: tuple[str, ...] | None = None) -> None:
    """Raise ``ValueError`` if the command looks unsafe.

    *allowed_prefixes*: if set, the executable (``argv[0]`` basename) must start with one of these
    (e.g. ``("python", "pytest")``). Empty *argv* is rejected.
    """

    if not argv:
        raise ValueError("empty command")
    joined = " ".join(shlex.quote(a) for a in argv)
    if _DANGEROUS.search(joined):
        raise ValueError("command matches unsafe pattern")
    if allowed_prefixes:
        exe = argv[0].replace("\\", "/").split("/")[-1].lower()
        if not any(exe.startswith(p.lower()) for p in allowed_prefixes):
            raise ValueError(f"executable not allowed: {exe!r}")
