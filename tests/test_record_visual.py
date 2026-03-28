"""record_visual module (no Playwright run)."""

from __future__ import annotations

import subprocess
import sys

import paper_pipeline.record_visual as rv


def test_record_visual_has_main() -> None:
    assert hasattr(rv, "main")


def test_record_visual_exits_when_playwright_missing() -> None:
    script = r"""
import builtins
_real = builtins.__import__
def _i(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "playwright" or (isinstance(name, str) and name.startswith("playwright.")):
        raise ImportError("no playwright in test")
    return _real(name, globals, locals, fromlist, level)
builtins.__import__ = _i
import paper_pipeline.record_visual as r
r.main()
"""
    r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)
    assert r.returncode == 1
    combined = r.stderr + r.stdout
    assert "Playwright" in combined or "playwright" in combined.lower()
