"""Goal selection V1 based on ObjectiveState + ResearchMemory."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from paper_pipeline.agent.goals import ensure_goals_seed, try_goal_override_from_tree
from paper_pipeline.agent.strategic_memory import update_strategic_memory_artifacts

GOAL_SELECTION_NAME = "goal_selection.json"
GoalType = Literal["literature", "verification", "writing", "experiment", "wait_human", "stop"]


class GoalSelectionInputs(BaseModel):
    objective_state: dict[str, Any] = Field(default_factory=dict)
    memory_index: dict[str, Any] = Field(default_factory=dict)
    safety_latest: dict[str, Any] = Field(default_factory=dict)
    loop_state: dict[str, Any] = Field(default_factory=dict)


class GoalSelection(BaseModel):
    version: int = 1
    selected_goal_type: GoalType
    goal_text: str
    priority: float
    reason: str
    source_signals: list[str] = Field(default_factory=list)
    gates: dict[str, bool] = Field(default_factory=dict)
    last_updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def save_goal_selection(output_dir: Path, selection: GoalSelection) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / GOAL_SELECTION_NAME
    path.write_text(
        json.dumps(selection.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def load_goal_selection(path: Path) -> GoalSelection:
    data = json.loads(path.read_text(encoding="utf-8"))
    return GoalSelection.model_validate(data)


class GoalSelector:
    """Pure recommendation layer over objective and memory artifacts."""

    def select(self, inputs: GoalSelectionInputs) -> GoalSelection:
        objective = inputs.objective_state
        memory = inputs.memory_index
        gates = dict(objective.get("gates") or {})
        terms = dict(objective.get("terms") or {})
        latest_by_kind = dict(memory.get("latest_by_kind") or {})

        if gates.get("loop_stopped"):
            return GoalSelection(
                selected_goal_type="wait_human",
                goal_text="Pedir intervención humana tras parada por stall.",
                priority=1.0,
                reason="El loop se detuvo; conviene revisión humana antes de seguir.",
                source_signals=["objective_state.json", "loop/stop_decision.json"],
                gates=gates,
            )

        if gates.get("requires_human_approval"):
            return GoalSelection(
                selected_goal_type="wait_human",
                goal_text="Esperar aprobación humana para continuar.",
                priority=1.0,
                reason="El estado requiere aprobación humana explícita.",
                source_signals=["objective_state.json", "safety_trace.jsonl"],
                gates=gates,
            )

        latest_publish = latest_by_kind.get("publish") or {}
        latest_publish_payload = latest_publish.get("payload") or {}
        if objective.get("status") == "blocked" or latest_publish_payload.get("eligible_for_publication") is False:
            return GoalSelection(
                selected_goal_type="verification",
                goal_text="Verificar bloqueos, claims y evidencia antes de seguir.",
                priority=0.9,
                reason="La publicación no es elegible o quedó bloqueada.",
                source_signals=["objective_state.json", "memory_index.json", "publication/publish_decision.json"],
                gates=gates,
            )

        contribution = float(terms.get("contribution_estimate") or 0.0)
        if gates.get("publishable") and contribution >= 0.6:
            return GoalSelection(
                selected_goal_type="writing",
                goal_text="Consolidar borrador y preparar verificación editorial/final.",
                priority=0.8,
                reason="Hay contribución suficiente y publicación elegible.",
                source_signals=["objective_state.json", "publication/publish_decision.json"],
                gates=gates,
            )

        if objective.get("status") == "healthy" and contribution > 0:
            return GoalSelection(
                selected_goal_type="experiment",
                goal_text="Ejecutar un siguiente experimento acotado para mejorar evidencia.",
                priority=0.7,
                reason="El estado es sano y aún hay margen de mejora empírica.",
                source_signals=["objective_state.json", "memory_index.json"],
                gates=gates,
            )

        return GoalSelection(
            selected_goal_type="literature",
            goal_text="Explorar literatura y contraejemplos para reducir incertidumbre.",
            priority=0.6,
            reason="No hay una señal fuerte para ejecutar publicación o experimento inmediato.",
            source_signals=["objective_state.json", "memory_index.json"],
            gates=gates,
        )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def build_goal_selection_from_output_dir(output_dir: Path) -> GoalSelection:
    override = try_goal_override_from_tree(output_dir)
    if override is not None:
        return override
    inputs = GoalSelectionInputs(
        objective_state=_read_json(output_dir / "objective_state.json"),
        memory_index=_read_json(output_dir / "memory_index.json"),
        safety_latest={},
        loop_state=_read_json(output_dir / "loop" / "loop_state.json"),
    )
    return GoalSelector().select(inputs)


def update_goal_selection_artifacts(output_dir: Path) -> tuple[Path, GoalSelection]:
    ensure_goals_seed(output_dir)
    selection = build_goal_selection_from_output_dir(output_dir)
    path = save_goal_selection(output_dir, selection)
    update_strategic_memory_artifacts(output_dir, selection)
    return path, selection


def resolve_goal_text(output_dir: Path, *, explicit_goal: str, default_goal: str) -> str:
    if explicit_goal.strip():
        return explicit_goal.strip()
    path = output_dir / GOAL_SELECTION_NAME
    if path.is_file():
        try:
            selection = load_goal_selection(path)
            if selection.goal_text.strip():
                return selection.goal_text.strip()
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    return default_goal

