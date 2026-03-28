"""ObjectiveState V1: auditable objective consolidation from existing artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

OBJECTIVE_STATE_NAME = "objective_state.json"
DEFAULT_ROOT_OBJECTIVE = "Maximizar evidencia reproducible de una contribución publicable"
ObjectiveStatus = Literal["healthy", "blocked", "stalled", "needs_review"]


class ObjectiveInputs(BaseModel):
    root_objective: str
    quality_validation: dict[str, Any] = Field(default_factory=dict)
    triage_report: dict[str, Any] = Field(default_factory=dict)
    publish_decision: dict[str, Any] = Field(default_factory=dict)
    run_ledger: dict[str, Any] = Field(default_factory=dict)
    loop_stop_decision: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    safety_latest: dict[str, Any] = Field(default_factory=dict)
    source_artifacts: list[str] = Field(default_factory=list)


class ObjectiveState(BaseModel):
    version: int = 1
    root_objective: str
    status: ObjectiveStatus
    utility_total: float
    terms: dict[str, float]
    gates: dict[str, bool]
    source_artifacts: list[str] = Field(default_factory=list)
    last_updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def save_objective_state(output_dir: Path, state: ObjectiveState) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / OBJECTIVE_STATE_NAME
    path.write_text(json.dumps(state.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_objective_state(path: Path) -> ObjectiveState:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ObjectiveState.model_validate(data)


class ObjectiveBuilder:
    """Build a compact objective state from already-produced artifacts."""

    def build(self, inputs: ObjectiveInputs) -> ObjectiveState:
        qv = inputs.quality_validation
        tr = inputs.triage_report
        pub = inputs.publish_decision
        ledger = inputs.run_ledger
        loop_stop = inputs.loop_stop_decision
        safety = inputs.safety_latest

        blocking_reasons = list(qv.get("blocking_reasons") or []) + list(pub.get("blocking_reasons") or [])
        metrics_validation_errors = list(tr.get("metrics_validation_errors") or [])
        metrics_valid = len(metrics_validation_errors) == 0
        publishable = bool(pub.get("eligible_for_publication", qv.get("publishable", False)))
        loop_stopped = bool(loop_stop)
        requires_human_approval = safety.get("decision") == "REQUIRE_HUMAN_APPROVAL"

        tier = tr.get("tier")
        contribution_estimate = 0.0
        if tier == 3:
            contribution_estimate = 1.0
        elif tier == 2:
            contribution_estimate = 0.6
        elif tier == 1:
            contribution_estimate = -0.3
        elif tier == 0:
            contribution_estimate = -0.7

        quality_score = 1.0 if qv.get("publishable") else (-0.5 if blocking_reasons else 0.0)

        phase_count = len(ledger.get("phases") or [])
        cost_score = min(1.0, phase_count / 20) if phase_count else 0.1
        if loop_stopped:
            cost_score += 0.5

        risk_score = 0.0
        if blocking_reasons:
            risk_score += 0.8
        if metrics_validation_errors:
            risk_score += 0.7
        if tr.get("metrics_relax_mode"):
            risk_score += 0.2
        if requires_human_approval:
            risk_score += 0.4

        coherence_score = 1.0
        if publishable and tier == 0:
            coherence_score -= 0.6
        if loop_stopped:
            coherence_score -= 0.9
        if blocking_reasons and publishable:
            coherence_score -= 0.5
        coherence_score = max(-1.0, coherence_score)

        utility_total = round(
            contribution_estimate + quality_score + coherence_score - cost_score - risk_score,
            3,
        )

        status: ObjectiveStatus = "healthy"
        if loop_stopped:
            status = "stalled"
        elif blocking_reasons or metrics_validation_errors:
            status = "blocked"
        elif requires_human_approval:
            status = "needs_review"

        source_artifacts = list(inputs.source_artifacts)
        if not source_artifacts:
            source_artifacts = [
                *(
                    ["validation/quality_validation.json"]
                    if qv
                    else []
                ),
                *(
                    ["triage/triage_report.json"]
                    if tr
                    else []
                ),
                *(
                    ["publication/publish_decision.json"]
                    if pub
                    else []
                ),
                *(
                    ["run_ledger.json"]
                    if ledger
                    else []
                ),
                *(
                    ["loop/stop_decision.json"]
                    if loop_stop
                    else []
                ),
                *(
                    ["safety_trace.jsonl"]
                    if safety
                    else []
                ),
            ]

        return ObjectiveState(
            root_objective=inputs.root_objective,
            status=status,
            utility_total=utility_total,
            terms={
                "contribution_estimate": float(contribution_estimate),
                "quality_score": float(quality_score),
                "cost_score": float(round(cost_score, 3)),
                "risk_score": float(round(risk_score, 3)),
                "coherence_score": float(round(coherence_score, 3)),
            },
            gates={
                "metrics_valid": metrics_valid,
                "publishable": publishable,
                "loop_stopped": loop_stopped,
                "requires_human_approval": requires_human_approval,
            },
            source_artifacts=source_artifacts,
        )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_last_jsonl(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return {}


def build_objective_state_from_output_dir(
    output_dir: Path,
    *,
    root_objective: str = DEFAULT_ROOT_OBJECTIVE,
) -> ObjectiveState:
    inputs = ObjectiveInputs(
        root_objective=root_objective,
        quality_validation=_read_json(output_dir / "validation" / "quality_validation.json"),
        triage_report=_read_json(output_dir / "triage" / "triage_report.json"),
        publish_decision=_read_json(output_dir / "publication" / "publish_decision.json"),
        run_ledger=_read_json(output_dir / "run_ledger.json"),
        loop_stop_decision=_read_json(output_dir / "loop" / "stop_decision.json"),
        metrics=_read_json(output_dir / "metrics.json"),
        safety_latest=_read_last_jsonl(output_dir / "safety_trace.jsonl"),
    )
    return ObjectiveBuilder().build(inputs)


def update_objective_artifacts(
    output_dir: Path,
    *,
    candidate_action_family: str,
    root_objective: str = DEFAULT_ROOT_OBJECTIVE,
) -> tuple[Path, Path, ObjectiveState]:
    from paper_pipeline.agent.objective_trace import append_objective_trace

    state = build_objective_state_from_output_dir(output_dir, root_objective=root_objective)
    state_path = save_objective_state(output_dir, state)
    trace_path = append_objective_trace(
        output_dir,
        state,
        candidate_action_family=candidate_action_family,
    )
    return state_path, trace_path, state

