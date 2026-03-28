"""Ruta y URL del mock estático visual-flow (compartido por grabación y tests E2E)."""

from __future__ import annotations

from pathlib import Path


def visual_flow_index_path() -> Path:
    return Path(__file__).resolve().parents[1] / "visual-flow" / "index.html"


def visual_flow_file_url() -> str:
    p = visual_flow_index_path()
    if not p.is_file():
        raise FileNotFoundError(p)
    return p.as_uri()
