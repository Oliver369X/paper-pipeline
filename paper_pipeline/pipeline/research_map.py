"""Research map state for long-horizon missions."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission


def default_research_map(mission: Mission) -> dict[str, Any]:
    nodes = [
        {"id": "literature", "status": "pending", "label": "Literature review"},
        {"id": "experiment", "status": "pending", "label": "Experiments"},
        {"id": "writing", "status": "pending", "label": "Writing"},
        {"id": "blocked", "status": "inactive", "label": "Blocked"},
    ]
    return {
        "schema_version": 1,
        "topic": mission.topic,
        "updated_at": datetime.now(UTC).isoformat(),
        "nodes": nodes,
    }


def update_research_map_from_outputs(out: Path, mission: Mission) -> dict[str, Any]:
    data = default_research_map(mission)
    nodes = {n["id"]: n for n in data["nodes"]}

    if any(out.glob("*.md")):
        nodes["literature"]["status"] = "done"
    if (out / "metrics.json").is_file():
        nodes["experiment"]["status"] = "done"
    elif mission.enable_experiment_runner:
        nodes["experiment"]["status"] = "in_progress"
    if (out / "draft_paper.md").is_file():
        nodes["writing"]["status"] = "done"

    state_path = out / "run_state.json"
    if state_path.is_file():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            errs = st.get("errors")
            if isinstance(errs, list) and errs:
                nodes["blocked"]["status"] = "active"
        except (OSError, json.JSONDecodeError):
            pass

    data["nodes"] = list(nodes.values())
    data["updated_at"] = datetime.now(UTC).isoformat()
    return data


def write_research_map(out: Path, mission: Mission) -> Path:
    data = update_research_map_from_outputs(out, mission)
    p = out / "research_map.json"
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
