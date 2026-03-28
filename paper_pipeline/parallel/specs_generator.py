"""Generate ``paper-parallel`` batch specs from mission hypotheses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission


def specs_from_mission(mission: Mission, *, command_template: list[str] | None = None) -> list[dict[str, Any]]:
    """Return a JSON-serializable list of AgentRunSpec-like dicts."""

    if not mission.hypotheses:
        return []

    default_cmd = command_template or ["python", "-c", "print('noop')"]
    out: list[dict[str, Any]] = []
    for hyp in mission.hypotheses:
        mission_md = (
            "---\n"
            f"topic: {mission.topic!r}\n"
            f"paper_target: {mission.paper_target!r}\n"
            f"output_dir: outputs\n"
            "---\n"
        )
        out.append(
            {
                "exp_id": hyp.id,
                "hypothesis": hyp.description,
                "mission_md_content": mission_md,
                "command": list(default_cmd),
                "branch_name": f"exp/{hyp.id}",
            }
        )
    return out


def write_specs_json(path: Path, mission: Mission) -> Path:
    data = specs_from_mission(mission)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
