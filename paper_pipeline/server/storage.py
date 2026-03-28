"""Filesystem CRUD for missions."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from paper_pipeline.mission import (
    ExperimentRunnerConfig,
    ExperimentRunnerPatch,
    Hypothesis,
    Mission,
    load_mission,
    normalize_hypothesis_dict_list,
    save_mission,
)

from .paths import data_root, mission_dir
from .schemas import MissionCreate, MissionMeta, MissionPatch, QualityGatesPatch
from .section_keys import normalize_sections_needed


def ensure_data_root() -> None:
    data_root().mkdir(parents=True, exist_ok=True)


def list_mission_ids() -> list[str]:
    ensure_data_root()
    out: list[str] = []
    for p in sorted(data_root().iterdir()):
        if p.is_dir() and (p / "mission.md").is_file():
            out.append(p.name)
    return out


def create_mission(body: MissionCreate) -> str:
    ensure_data_root()
    mid = uuid.uuid4().hex[:12]
    root = mission_dir(mid)
    root.mkdir(parents=True, exist_ok=True)
    out_abs = root / "outputs"
    out_abs.mkdir(parents=True, exist_ok=True)
    (root / "web").mkdir(exist_ok=True)
    (root / "web" / "draft_snapshots").mkdir(exist_ok=True)

    meta = MissionMeta(title=body.title, description=body.description)
    (root / "meta.json").write_text(
        json.dumps(meta.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    er = ExperimentRunnerConfig()
    if body.experiment_runner is not None:
        er = er.model_copy(update=body.experiment_runner.model_dump(exclude_unset=True))

    mission = Mission(
        mission_version=body.mission_version,
        topic=body.topic,
        paper_target=body.paper_target,
        sections_needed=normalize_sections_needed(body.sections_needed),
        max_perplexity_calls=body.max_perplexity_calls,
        code_needed=body.code_needed,
        notion_page_id=body.notion_page_id,
        model=body.model,
        language=body.language,
        output_dir=str(out_abs.resolve()),
        enable_notion=body.enable_notion,
        enable_quality_check=body.enable_quality_check,
        enable_cursor_cli=body.enable_cursor_cli,
        cursor_cli_optional=body.cursor_cli_optional,
        single_thread_perplexity=body.single_thread_perplexity,
        save_perplexity_to_library=body.save_perplexity_to_library,
        enable_epistemic_injection=body.enable_epistemic_injection,
        enable_degradation_monitor=body.enable_degradation_monitor,
        enable_skill_orchestrator=body.enable_skill_orchestrator,
        enable_hypervisor_triage=body.enable_hypervisor_triage,
        enable_experiment_runner=body.enable_experiment_runner,
        experiment_runner=er,
        parallel_allowed_command_prefixes=body.parallel_allowed_command_prefixes,
    )
    save_mission(mission, root / "mission.md")
    return mid


def read_meta(mid: str) -> MissionMeta:
    p = mission_dir(mid) / "meta.json"
    if not p.is_file():
        return MissionMeta()
    data = json.loads(p.read_text(encoding="utf-8"))
    return MissionMeta.model_validate(data)


def write_meta(mid: str, meta: MissionMeta) -> None:
    p = mission_dir(mid) / "meta.json"
    p.write_text(json.dumps(meta.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")


def read_mission(mid: str) -> Mission:
    return load_mission(mission_dir(mid) / "mission.md")


def update_mission(mid: str, body: MissionPatch) -> None:
    """Apply a partial patch: only fields set in the request body are updated."""
    root = mission_dir(mid)
    out_abs = root / "outputs"
    out_abs.mkdir(parents=True, exist_ok=True)

    raw = body.model_dump(exclude_unset=True)

    meta = read_meta(mid)
    if "title" in raw:
        meta.title = str(raw.pop("title"))
    if "description" in raw:
        meta.description = str(raw.pop("description"))
    write_meta(mid, meta)

    existing = load_mission(root / "mission.md")
    mission_updates: dict[str, object] = {}

    if "quality_gates" in raw:
        qg_raw = raw.pop("quality_gates")
        patch_qg = QualityGatesPatch.model_validate(qg_raw)
        partial = patch_qg.model_dump(exclude_unset=True)
        if partial:
            mission_updates["quality_gates"] = existing.quality_gates.model_copy(update=partial)

    if "hypotheses" in raw:
        hy_raw = raw.pop("hypotheses")
        if isinstance(hy_raw, list):
            coerced = normalize_hypothesis_dict_list(hy_raw)
            mission_updates["hypotheses"] = [Hypothesis.model_validate(x) for x in coerced]
        else:
            mission_updates["hypotheses"] = []

    if "experiment_runner" in raw:
        er_raw = raw.pop("experiment_runner")
        patch_er = ExperimentRunnerPatch.model_validate(er_raw)
        partial = patch_er.model_dump(exclude_unset=True)
        if partial:
            mission_updates["experiment_runner"] = existing.experiment_runner.model_copy(update=partial)

    for key, value in raw.items():
        if key == "sections_needed":
            mission_updates[key] = normalize_sections_needed(value)
        else:
            mission_updates[key] = value

    if not mission_updates:
        return

    merged = existing.model_copy(update=mission_updates)
    save_mission(merged, root / "mission.md")


def read_triage_report(mid: str) -> dict | None:
    """Last triage report if ``outputs/triage/triage_report.json`` exists."""

    p = mission_dir(mid) / "outputs" / "triage" / "triage_report.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def read_metrics_json(mid: str) -> dict | None:
    """Experiment metrics if ``outputs/metrics.json`` exists."""

    p = mission_dir(mid) / "outputs" / "metrics.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def read_run_state(mid: str) -> dict | None:
    p = mission_dir(mid) / "outputs" / "run_state.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def last_run_error(mid: str) -> str | None:
    p = mission_dir(mid) / "outputs" / "run.log"
    if not p.is_file():
        return None
    last_err = None
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("event") == "step_error":
            last_err = rec.get("error") or str(rec)
    return last_err


def append_directive_history(mid: str, entry: dict) -> None:
    p = mission_dir(mid) / "web" / "directive_history.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {**entry, "ts": datetime.now(UTC).isoformat()}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def next_snapshot_path(mid: str) -> Path:
    snap_dir = mission_dir(mid) / "web" / "draft_snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(snap_dir.glob("v*.md")))
    return snap_dir / f"v{n + 1:03d}.md"


def read_draft(mid: str) -> str:
    p = mission_dir(mid) / "outputs" / "draft_paper.md"
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")


def write_brain_brief(mid: str, markdown: str) -> None:
    """Persist high-level domain brief from the brain (Gemini)."""

    p = mission_dir(mid) / "outputs" / "brain_brief.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).isoformat()
    header = f"<!-- brain_brief ts={ts} -->\n\n"
    p.write_text(header + markdown.strip() + "\n", encoding="utf-8")


def read_brain_brief(mid: str) -> str | None:
    """Return body text of ``outputs/brain_brief.md`` without the HTML comment header."""

    p = mission_dir(mid) / "outputs" / "brain_brief.md"
    if not p.is_file():
        return None
    raw = p.read_text(encoding="utf-8")
    if raw.startswith("<!--"):
        end = raw.find("-->")
        if end != -1:
            raw = raw[end + 3 :].lstrip()
    text = raw.strip()
    return text or None


def _brain_chat_history_path(mid: str) -> Path:
    return mission_dir(mid) / "outputs" / "brain_chat_history.jsonl"


def read_brain_chat_history(mid: str, *, limit: int = 200) -> list[dict[str, object]]:
    """Last *limit* JSON lines from ``outputs/brain_chat_history.jsonl``."""

    p = _brain_chat_history_path(mid)
    if not p.is_file():
        return []
    lines: list[str] = []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    parsed: list[dict[str, object]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            parsed.append(rec)
    if len(parsed) <= limit:
        return parsed
    return parsed[-limit:]


def append_brain_chat_turn(mid: str, *, user_content: str, assistant_content: str) -> None:
    """Append one user line and one assistant line (append-only)."""

    p = _brain_chat_history_path(mid)
    p.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).isoformat()
    with p.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {"ts": ts, "role": "user", "content": user_content},
                ensure_ascii=False,
            )
            + "\n"
        )
        fh.write(
            json.dumps(
                {"ts": ts, "role": "assistant", "content": assistant_content},
                ensure_ascii=False,
            )
            + "\n"
        )


def clear_brain_chat_history(mid: str) -> None:
    p = _brain_chat_history_path(mid)
    if p.is_file():
        p.unlink()


def write_brain_conversation_export(mid: str) -> Path:
    """Escribe ``outputs/brain_export_YYYYMMDD_HHMMSS.md`` con el historial del cerebro (consulta posterior)."""

    rows = read_brain_chat_history(mid, limit=5000)
    root = mission_dir(mid)
    out_dir = root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"brain_export_{ts}.md"
    lines: list[str] = [
        "# Export conversación — Cerebro (Gemini)\n\n",
        f"- **Misión:** `{mid}`\n",
        f"- **Generado (UTC):** {datetime.now(UTC).isoformat()}\n",
        f"- **Líneas en historial:** {len(rows)}\n\n",
        "---\n\n",
    ]
    for r in rows:
        role = str(r.get("role") or "?")
        ts_line = str(r.get("ts") or "")
        content = str(r.get("content") or "")
        lines.append(f"## {role} ({ts_line})\n\n{content}\n\n")
    path.write_text("".join(lines), encoding="utf-8")
    latest = out_dir / "brain_latest_export.md"
    try:
        latest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    except OSError:
        pass
    return path


def write_draft(mid: str, content: str) -> None:
    p = mission_dir(mid) / "outputs" / "draft_paper.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def read_pipeline_events(mid: str) -> list[dict]:
    """Structured events from ``outputs/pipeline_events.jsonl`` if present."""

    p = mission_dir(mid) / "outputs" / "pipeline_events.jsonl"
    if not p.is_file():
        return []
    rows: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def read_run_log_lines(mid: str) -> list[dict]:
    p = mission_dir(mid) / "outputs" / "run.log"
    if not p.is_file():
        return []
    rows: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def list_snapshots(mid: str) -> list[str]:
    snap_dir = mission_dir(mid) / "web" / "draft_snapshots"
    if not snap_dir.is_dir():
        return []
    return sorted(p.name for p in snap_dir.glob("v*.md"))


def read_snapshot(mid: str, name: str) -> str:
    p = mission_dir(mid) / "web" / "draft_snapshots" / name
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")
