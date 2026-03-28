"""Goal Manager V1: persistent goal tree (goals.json) and selection override."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

GOALS_NAME = "goals.json"

GoalNodeStatus = Literal["pending", "in_progress", "done", "abandoned"]


class GoalNode(BaseModel):
    id: str
    parent_id: str | None = None
    description: str
    goal_type: str
    status: GoalNodeStatus
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    source_artifacts: list[str] = Field(default_factory=list)


class GoalsDocument(BaseModel):
    version: int = 1
    nodes: list[GoalNode] = Field(default_factory=list)
    mission_topic_hint: str = ""


def goals_path(output_dir: Path) -> Path:
    return output_dir / GOALS_NAME


def load_goals_document(output_dir: Path) -> GoalsDocument | None:
    p = goals_path(output_dir)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return GoalsDocument.model_validate(data)


def save_goals_document(output_dir: Path, doc: GoalsDocument) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    p = goals_path(output_dir)
    p.write_text(json.dumps(doc.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def _mission_topic(output_dir: Path) -> str:
    mission_path = output_dir.parent / "mission.md"
    if not mission_path.is_file():
        return "research"
    try:
        from paper_pipeline.mission import load_mission

        return load_mission(mission_path).topic
    except Exception:
        return "research"


def ensure_goals_seed(output_dir: Path) -> Path:
    """Create ``goals.json`` with one pending root node if missing."""
    if goals_path(output_dir).is_file():
        return goals_path(output_dir)
    topic = _mission_topic(output_dir)
    doc = GoalsDocument(
        mission_topic_hint=topic,
        nodes=[
            GoalNode(
                id="root-1",
                parent_id=None,
                description=f"Exploración inicial de literatura sobre: {topic}",
                goal_type="literature",
                status="pending",
                priority=0.5,
                source_artifacts=["goals.json"],
            )
        ],
    )
    return save_goals_document(output_dir, doc)


def try_goal_override_from_tree(output_dir: Path):
    """If a node is ``in_progress``, return a ``GoalSelection`` aligned to it; else None."""
    from paper_pipeline.agent.goal_selection import GoalSelection

    doc = load_goals_document(output_dir)
    if doc is None:
        return None
    active = next((n for n in doc.nodes if n.status == "in_progress"), None)
    if active is None:
        return None

    valid_types = frozenset({"literature", "verification", "writing", "experiment", "wait_human", "stop"})
    if active.goal_type not in valid_types:
        return None

    objective: dict = {}
    op = output_dir / "objective_state.json"
    if op.is_file():
        try:
            objective = json.loads(op.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            objective = {}
    gates = dict(objective.get("gates") or {})

    return GoalSelection(
        selected_goal_type=active.goal_type,  # type: ignore[arg-type]
        goal_text=active.description,
        priority=float(active.priority),
        reason="Meta explícita en progreso según goals.json.",
        source_signals=["goals.json", active.id],
        gates=gates,
    )


def update_goals_artifacts(output_dir: Path) -> Path | None:
    """Seed goals file if missing (idempotent)."""
    return ensure_goals_seed(output_dir)
