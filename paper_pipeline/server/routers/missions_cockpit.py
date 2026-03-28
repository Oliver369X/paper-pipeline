"""Ledger, evidence, triage, claims, publish-preview API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from paper_pipeline.server.paths import mission_dir
from paper_pipeline.server.schemas import MemoryCompactRequest, RunAgentStepRequest

router = APIRouter()


def _read_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _read_last_jsonl(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None


@router.get("/{mission_id}/ledger/latest")
def get_ledger_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    out = root / "outputs"
    p = out / "run_ledger.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "run_ledger.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid ledger")
    return data


@router.get("/{mission_id}/evidence/latest")
def get_evidence_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    idx = root / "outputs" / "evidence" / "evidence_index.json"
    data = _read_json(idx)
    if data is None:
        raise HTTPException(404, "evidence bundle not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid evidence index")
    return data


@router.get("/{mission_id}/claims/latest")
def get_claims_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "evidence" / "claims.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "claims.json not found")
    return {"claims": data}


@router.get("/{mission_id}/diagnostics/latest")
def get_diagnostics_latest(mission_id: str) -> dict:
    """Resumen de fallos empíricos / CLI: ``metrics.json``, diagnósticos y ``replication_status.md``."""

    root = mission_dir(mission_id)
    out = root / "outputs"
    metrics = _read_json(out / "metrics.json")
    cursor_d = _read_json(out / "cursor_cli_diagnostics.json")
    exp_d = _read_json(out / "experiment_diagnostics.json")
    repl: dict[str, str] = {}
    rp = out / "replication_status.md"
    if rp.is_file():
        try:
            repl["markdown"] = rp.read_text(encoding="utf-8")[:12_000]
        except OSError:
            pass
    prov = _read_json(out / "pipeline_provenance.json")
    prompt_last = out / "cursor_cli_prompt_last.txt"
    prov_extra: dict[str, Any] = {}
    if isinstance(prov, dict):
        prov_extra = dict(prov)
    if prompt_last.is_file():
        prov_extra["cursor_cli_prompt_last_bytes"] = prompt_last.stat().st_size

    return {
        "metrics": metrics,
        "cursor_cli_diagnostics": cursor_d,
        "experiment_diagnostics": exp_d,
        "replication_status": repl or None,
        "pipeline_provenance": prov if isinstance(prov, dict) else None,
        "pipeline_provenance_extra": prov_extra or None,
    }


@router.get("/{mission_id}/triage/latest")
def get_triage_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "triage" / "triage_report.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "triage report not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid triage")
    return data


@router.post("/{mission_id}/publish/preview")
def post_publish_preview(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "publication" / "publish_decision.json"
    data = _read_json(p)
    if data is None:
        return {"eligible": False, "reason": "no publish_decision.json — run pipeline first"}
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid publish decision")
    return {
        "eligible": bool(data.get("eligible_for_publication")),
        "blocking_reasons": data.get("blocking_reasons", []),
    }


@router.get("/{mission_id}/publish/decision")
def get_publish_decision(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "publication" / "publish_decision.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "publish_decision.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid publish decision")
    return data


@router.get("/{mission_id}/loop/stop")
def get_loop_stop(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "loop" / "stop_decision.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "stop_decision.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid stop decision")
    return data


@router.get("/{mission_id}/metrics/validated")
def get_metrics_validated(mission_id: str) -> dict:
    from paper_pipeline.evidence.metrics_io import load_and_validate_metrics

    root = mission_dir(mission_id)
    mpath = root / "outputs" / "metrics.json"
    if not mpath.is_file():
        raise HTTPException(404, "metrics.json not found")
    bundle, errors = load_and_validate_metrics(mpath)
    return {"ok": bundle is not None, "errors": errors}


@router.get("/{mission_id}/safety/latest")
def get_safety_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "safety_trace.jsonl"
    data = _read_last_jsonl(p)
    if data is None:
        raise HTTPException(404, "safety_trace.jsonl not found")
    return data


@router.get("/{mission_id}/objective/latest")
def get_objective_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "objective_state.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "objective_state.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid objective state")
    return data


@router.get("/{mission_id}/memory/latest")
def get_memory_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "research_memory.jsonl"
    data = _read_last_jsonl(p)
    if data is None:
        raise HTTPException(404, "research_memory.jsonl not found")
    return data


@router.get("/{mission_id}/memory/index")
def get_memory_index(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "memory_index.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "memory_index.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid memory index")
    return data


@router.get("/{mission_id}/goal-selection/latest")
def get_goal_selection_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "goal_selection.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "goal_selection.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid goal selection")
    return data


@router.get("/{mission_id}/goals/latest")
def get_goals_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "goals.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "goals.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid goals document")
    return data


@router.get("/{mission_id}/working-memory/latest")
def get_working_memory_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "working_memory.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "working_memory.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid working memory")
    return data


@router.get("/{mission_id}/hypotheses/latest")
def get_hypotheses_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "hypotheses_registry.json"
    data = _read_json(p)
    if data is None:
        raise HTTPException(404, "hypotheses_registry.json not found")
    if not isinstance(data, dict):
        raise HTTPException(500, "invalid hypotheses registry")
    return data


@router.get("/{mission_id}/agent/decisions/latest")
def get_agent_decisions_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "agent_decisions.jsonl"
    data = _read_last_jsonl(p)
    if data is None:
        raise HTTPException(404, "agent_decisions.jsonl not found")
    return data


@router.get("/{mission_id}/perplexity/calls/latest")
def get_perplexity_calls_latest(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    p = root / "outputs" / "perplexity_call_record.jsonl"
    data = _read_last_jsonl(p)
    if data is None:
        raise HTTPException(404, "perplexity_call_record.jsonl not found")
    return data


@router.get("/{mission_id}/memory/query")
def get_memory_query(
    mission_id: str,
    goal_type: str = Query(..., min_length=1, max_length=64),
    limit: int = Query(default=30, ge=1, le=200),
) -> dict:
    from paper_pipeline.agent.research_memory import query_memory_entries_for_goal

    root = mission_dir(mission_id)
    out = root / "outputs"
    entries = query_memory_entries_for_goal(out, goal_type, limit=limit)
    return {"goal_type": goal_type, "limit": limit, "entries": entries, "count": len(entries)}


@router.post("/{mission_id}/memory/compact")
def post_memory_compact(mission_id: str, body: MemoryCompactRequest) -> dict:
    from paper_pipeline.agent.research_memory import compact_memory_dry_run

    root = mission_dir(mission_id)
    out = root / "outputs"
    report = compact_memory_dry_run(out)
    report["request_dry_run"] = body.dry_run
    return report


@router.post("/{mission_id}/agent/run-step")
def post_agent_run_step(mission_id: str, body: RunAgentStepRequest) -> dict:
    from paper_pipeline.agent.scheduler import run_agent_step
    from paper_pipeline.mission import load_mission

    root = mission_dir(mission_id)
    out = root / "outputs"
    mp = root / "mission.md"
    mission = None
    if mp.is_file():
        try:
            mission = load_mission(mp)
        except (OSError, ValueError):
            mission = None
    return run_agent_step(out, mission, dry_run=body.dry_run)


@router.post("/{mission_id}/parallel/specs/generate")
def post_parallel_specs_generate(mission_id: str) -> dict:
    from paper_pipeline.mission import load_mission
    from paper_pipeline.parallel.specs_generator import specs_from_mission

    root = mission_dir(mission_id)
    mp = root / "mission.md"
    if not mp.is_file():
        raise HTTPException(404, "mission.md not found")
    mission = load_mission(mp)
    specs = specs_from_mission(mission)
    path = root / "outputs" / "parallel" / "specs_generated.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(specs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"path": str(path), "count": len(specs), "specs": specs}
