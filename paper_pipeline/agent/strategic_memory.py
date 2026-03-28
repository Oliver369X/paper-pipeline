"""Strategic memory V2 (thin): working snapshot + hypotheses registry scaffold."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

WORKING_MEMORY_NAME = "working_memory.json"
HYPOTHESES_REGISTRY_NAME = "hypotheses_registry.json"

HypothesisStatus = Literal["open", "supported", "weakened", "rejected"]


class HypothesisEntry(BaseModel):
    id: str
    statement: str
    status: HypothesisStatus = "open"
    source_artifacts: list[str] = Field(default_factory=list)


class HypothesesRegistry(BaseModel):
    version: int = 1
    hypotheses: list[HypothesisEntry] = Field(default_factory=list)
    last_updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class WorkingMemoryState(BaseModel):
    version: int = 1
    current_goal_type: str
    goal_text_snapshot: str
    reason_snapshot: str
    recent_observations: list[str] = Field(default_factory=list)
    constraints: dict[str, Any] = Field(default_factory=dict)
    last_updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def save_working_memory(output_dir: Path, state: WorkingMemoryState) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / WORKING_MEMORY_NAME
    path.write_text(
        json.dumps(state.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def load_working_memory(path: Path) -> WorkingMemoryState | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return WorkingMemoryState.model_validate(data)


def save_hypotheses_registry(output_dir: Path, reg: HypothesesRegistry) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / HYPOTHESES_REGISTRY_NAME
    reg.last_updated_at = datetime.now(UTC).isoformat()
    path.write_text(
        json.dumps(reg.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def load_hypotheses_registry(path: Path) -> HypothesesRegistry | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return HypothesesRegistry.model_validate(data)


def ensure_hypotheses_registry(output_dir: Path) -> Path:
    """Ensure ``hypotheses_registry.json`` exists (empty list is valid)."""
    p = output_dir / HYPOTHESES_REGISTRY_NAME
    if p.is_file():
        return p
    return save_hypotheses_registry(output_dir, HypothesesRegistry())


def update_strategic_memory_artifacts(output_dir: Path, selection: object) -> tuple[Path, Path]:
    """Persist working memory from a ``GoalSelection`` and ensure hypotheses file."""
    from paper_pipeline.agent.goal_selection import GoalSelection

    if not isinstance(selection, GoalSelection):
        raise TypeError("selection must be GoalSelection")
    wm = WorkingMemoryState(
        current_goal_type=selection.selected_goal_type,
        goal_text_snapshot=selection.goal_text,
        reason_snapshot=selection.reason,
        recent_observations=[],
        constraints={},
    )
    wp = save_working_memory(output_dir, wm)
    hp = ensure_hypotheses_registry(output_dir)
    return wp, hp
