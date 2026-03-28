"""Mission list, export, create, get, patch."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..paths import mission_dir
from ..schemas import MissionCreate, MissionPatch
from .. import storage

router = APIRouter()


def _tsv_cell(value: object) -> str:
    s = "" if value is None else str(value)
    return s.replace("\t", " ").replace("\r", " ").replace("\n", " ")


@router.get("/")
def list_missions() -> list[dict]:
    storage.ensure_data_root()
    items: list[dict] = []
    for mid in storage.list_mission_ids():
        meta = storage.read_meta(mid)
        st = storage.read_run_state(mid)
        err = storage.last_run_error(mid)
        mission = storage.read_mission(mid)
        items.append(
            {
                "id": mid,
                "title": meta.title,
                "description": meta.description,
                "has_run_state": st is not None,
                "last_error": err,
                "flags_v2": {
                    "enable_epistemic_injection": mission.enable_epistemic_injection,
                    "enable_degradation_monitor": mission.enable_degradation_monitor,
                    "enable_skill_orchestrator": mission.enable_skill_orchestrator,
                    "enable_hypervisor_triage": mission.enable_hypervisor_triage,
                },
            },
        )
    return items


@router.get("/export.tsv")
def export_missions_tsv() -> Response:
    """Tab-separated overview of all missions (inspired by autoresearch ``results.tsv``)."""

    storage.ensure_data_root()
    header = [
        "id",
        "title",
        "topic",
        "paper_target",
        "has_run_state",
        "last_error",
        "triage_tier",
        "triage_label",
        "main_metric",
        "hypotheses_count",
        "epistemic",
        "degradation",
        "skills",
        "hypervisor_triage",
    ]
    lines = ["\t".join(header)]
    for mid in storage.list_mission_ids():
        meta = storage.read_meta(mid)
        st = storage.read_run_state(mid)
        err = storage.last_run_error(mid)
        mission = storage.read_mission(mid)
        triage = storage.read_triage_report(mid)
        metrics = storage.read_metrics_json(mid)
        tier = triage.get("tier") if triage else ""
        label = triage.get("label") if triage else ""
        main_m = ""
        if metrics:
            main_m = metrics.get("main", metrics.get("score", ""))
        if main_m == "" and triage:
            tm = triage.get("metrics") or {}
            main_m = tm.get("main", "")
        row = [
            mid,
            meta.title,
            mission.topic,
            mission.paper_target,
            "1" if st is not None else "0",
            err or "",
            tier,
            label,
            main_m,
            len(mission.hypotheses),
            mission.enable_epistemic_injection,
            mission.enable_degradation_monitor,
            mission.enable_skill_orchestrator,
            mission.enable_hypervisor_triage,
        ]
        lines.append("\t".join(_tsv_cell(x) for x in row))
    body = "\n".join(lines) + "\n"
    return Response(
        content=body.encode("utf-8"),
        media_type="text/tab-separated-values; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="paper-pipeline-missions.tsv"'},
    )


@router.post("/", status_code=201)
def create_mission(body: MissionCreate) -> dict:
    mid = storage.create_mission(body)
    return {"id": mid}


@router.get("/{mission_id}")
def get_mission(mission_id: str) -> dict:
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    meta = storage.read_meta(mission_id)
    m = storage.read_mission(mission_id)
    return {
        "id": mission_id,
        "meta": meta.model_dump(),
        "mission": m.model_dump(),
    }


@router.patch("/{mission_id}")
def patch_mission(mission_id: str, body: MissionPatch) -> dict:
    """Partial update: only JSON keys sent in the body are applied (see MissionPatch)."""
    root = mission_dir(mission_id)
    if not (root / "mission.md").is_file():
        raise HTTPException(404, "Mission not found")
    storage.update_mission(mission_id, body)
    return {"ok": True}
