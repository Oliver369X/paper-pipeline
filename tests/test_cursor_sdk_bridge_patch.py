"""Tests for Windows cursor-sdk bridge discovery patch."""

from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from paper_pipeline.cursor_sdk_bridge_patch import (
    _read_discovery_polling,
    apply_cursor_sdk_bridge_patch,
    ensure_cursor_sdk_ready,
)


def test_apply_patch_idempotent() -> None:
    if os.name != "nt":
        pytest.skip("Windows-only patch")
    assert apply_cursor_sdk_bridge_patch() is True
    assert apply_cursor_sdk_bridge_patch() is True
    import cursor_sdk._bridge as bridge_mod

    assert getattr(bridge_mod._read_discovery, "__paper_pipeline_patched__", False)


def test_read_discovery_polling_parses_ready_line() -> None:
    payload = (
        '{"schemaVersion":1,"transport":"tcp","protocol":"connect",'
        '"url":"http://127.0.0.1:9999","authToken":"tok"}'
    )
    line = f"cursor-sdk-bridge ready {payload}\n"

    proc = MagicMock(spec=subprocess.Popen)
    proc.stderr = MagicMock()
    proc.stderr.fileno.return_value = -1
    proc.poll.return_value = None

    read_chunks = [line.encode("utf-8"), b""]

    def fake_read(fd: int, n: int) -> bytes:
        if read_chunks:
            return read_chunks.pop(0)
        return b""

    with patch("paper_pipeline.cursor_sdk_bridge_patch.os.read", side_effect=fake_read):
        with patch("paper_pipeline.cursor_sdk_bridge_patch.os.get_blocking", return_value=True):
            with patch("paper_pipeline.cursor_sdk_bridge_patch.os.set_blocking"):
                discovery = _read_discovery_polling(proc, timeout=1.0)

    assert discovery["url"] == "http://127.0.0.1:9999"
    assert discovery["authToken"] == "tok"


def test_ensure_ready_noop_on_old_python(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "version_info", (3, 11, 0))
    ensure_cursor_sdk_ready()  # should not raise
