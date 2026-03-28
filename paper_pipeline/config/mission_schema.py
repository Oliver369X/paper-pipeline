"""JSON Schema export for Mission (documentation + external validators)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from paper_pipeline.mission import Mission


@lru_cache(maxsize=1)
def get_mission_json_schema() -> dict:
    """Return JSON Schema for the Mission model (Pydantic v2)."""

    return Mission.model_json_schema()


def write_mission_schema_file(path: Path | None = None) -> Path:
    """Write schemas/mission.schema.json next to repo root if path not given."""

    root = Path(__file__).resolve().parents[2]
    out = path or (root / "schemas" / "mission.schema.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(get_mission_json_schema(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out
