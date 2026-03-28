"""Resolve data directory for web UI missions."""

from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import HTTPException

_MISSION_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


def assert_safe_mission_id(mission_id: str) -> None:
    """Reject path traversal and invalid IDs (used by API layer)."""

    if not mission_id or ".." in mission_id or "/" in mission_id or "\\" in mission_id:
        raise HTTPException(400, "invalid mission id")
    if not _MISSION_ID_RE.fullmatch(mission_id):
        raise HTTPException(400, "invalid mission id")


def data_root() -> Path:
    raw = os.environ.get("PAPER_PIPELINE_DATA_DIR", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.cwd() / "data" / "missions").resolve()


def mission_dir(mission_id: str) -> Path:
    assert_safe_mission_id(mission_id)
    return data_root() / mission_id
