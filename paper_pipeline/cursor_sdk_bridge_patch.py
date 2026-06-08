"""Windows-compatible bridge discovery for cursor-sdk.

``cursor_sdk._bridge._read_discovery`` uses ``selectors.select`` on the bridge
process stderr pipe. On Windows that raises ``WinError 10038`` (not a socket).
We replace the wait loop with timed polling + ``os.read`` on a non-blocking fd,
matching the upstream drain logic without ``select``.
"""

from __future__ import annotations

import codecs
import logging
import os
import subprocess
import sys
import time
from typing import Any, Mapping

logger = logging.getLogger(__name__)

_PATCH_APPLIED = False


def _read_discovery_polling(
    process: subprocess.Popen[str], timeout: float
) -> Mapping[str, Any]:
    from cursor_sdk._bridge import parse_discovery_line
    from cursor_sdk.errors import CursorSDKError

    if process.stderr is None:
        raise CursorSDKError("Bridge process stderr is unavailable")
    stderr_fd = process.stderr.fileno()
    was_blocking = os.get_blocking(stderr_fd)
    os.set_blocking(stderr_fd, False)

    try:
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        deadline = time.monotonic() + timeout
        stderr_lines: list[str] = []
        pending = ""

        def drain_available() -> Mapping[str, Any] | None:
            nonlocal pending
            while True:
                try:
                    chunk = os.read(stderr_fd, 8192)
                except BlockingIOError:
                    return None
                if not chunk:
                    final_text = decoder.decode(b"", final=True)
                    if final_text:
                        pending += final_text
                    if pending:
                        line = pending
                        pending = ""
                        stderr_lines.append(line)
                        return parse_discovery_line(line)
                    return None
                pending += decoder.decode(chunk)
                while "\n" in pending:
                    line, pending = pending.split("\n", 1)
                    line += "\n"
                    stderr_lines.append(line)
                    discovery = parse_discovery_line(line)
                    if discovery is not None:
                        return discovery

        poll_interval = 0.05
        while time.monotonic() < deadline:
            discovery = drain_available()
            if discovery is not None:
                return discovery
            exit_code = process.poll()
            if exit_code is not None:
                discovery = drain_available()
                if discovery is not None:
                    return discovery
                raise CursorSDKError(
                    f"Bridge exited before discovery with status {exit_code}: "
                    + "".join(stderr_lines)
                    + pending
                )
            time.sleep(min(poll_interval, max(0.0, deadline - time.monotonic())))
        raise CursorSDKError("Timed out waiting for bridge discovery")
    finally:
        os.set_blocking(stderr_fd, was_blocking)


def apply_cursor_sdk_bridge_patch() -> bool:
    """Patch cursor-sdk bridge discovery on Windows. Idempotent."""

    global _PATCH_APPLIED
    if _PATCH_APPLIED:
        return True
    if os.name != "nt":
        return False
    try:
        import cursor_sdk._bridge as bridge_mod
    except ImportError:
        return False

    if getattr(bridge_mod._read_discovery, "__paper_pipeline_patched__", False):
        _PATCH_APPLIED = True
        return True

    bridge_mod._read_discovery = _read_discovery_polling  # type: ignore[assignment]
    _read_discovery_polling.__paper_pipeline_patched__ = True  # type: ignore[attr-defined]
    _PATCH_APPLIED = True
    logger.debug("Applied cursor-sdk Windows bridge discovery patch")
    return True


def ensure_cursor_sdk_ready() -> None:
    """Apply platform patches before any Agent/Client use."""

    if sys.version_info < (3, 12):
        return
    apply_cursor_sdk_bridge_patch()
