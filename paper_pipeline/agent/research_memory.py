"""ResearchMemory V1: append-only episodic memory plus cheap index."""

from __future__ import annotations

import json
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

RESEARCH_MEMORY_NAME = "research_memory.jsonl"
MEMORY_INDEX_NAME = "memory_index.json"
MemoryKind = Literal[
    "quality",
    "triage",
    "publish",
    "loop_stop",
    "run_consolidation",
    "brain_brief",
]


class ResearchMemoryEntry(BaseModel):
    ts: str
    memory_id: str
    kind: MemoryKind
    mission_id: str | None = None
    run_id: str | None = None
    summary: str
    confidence: float = 0.7
    source_artifacts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class MemoryIndex(BaseModel):
    version: int = 1
    counts_by_kind: dict[str, int] = Field(default_factory=dict)
    last_event: dict[str, Any] | None = None
    latest_by_kind: dict[str, dict[str, Any]] = Field(default_factory=dict)
    source_artifacts: list[str] = Field(default_factory=list)
    last_updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


def _memory_log_path(output_dir: Path) -> Path:
    return output_dir / RESEARCH_MEMORY_NAME


def _memory_index_path(output_dir: Path) -> Path:
    return output_dir / MEMORY_INDEX_NAME


def append_research_memory(
    output_dir: Path,
    *,
    kind: MemoryKind,
    summary: str,
    source_artifacts: list[str],
    payload: dict[str, Any],
    tags: list[str] | None = None,
    confidence: float = 0.7,
    mission_id: str | None = None,
    run_id: str | None = None,
) -> Path:
    """Append one normalized memory entry and refresh index."""
    output_dir.mkdir(parents=True, exist_ok=True)
    entry = ResearchMemoryEntry(
        ts=datetime.now(UTC).isoformat(),
        memory_id=uuid.uuid4().hex[:12],
        kind=kind,
        mission_id=mission_id,
        run_id=run_id,
        summary=summary,
        confidence=confidence,
        source_artifacts=source_artifacts,
        tags=tags or [],
        payload=payload,
    )
    path = _memory_log_path(output_dir)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.model_dump(mode="python"), ensure_ascii=False) + "\n")
    rebuild_memory_index(output_dir)
    return path


def _read_entries(output_dir: Path) -> list[dict[str, Any]]:
    path = _memory_log_path(output_dir)
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    entries: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            entries.append(data)
    return entries


def rebuild_memory_index(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    entries = _read_entries(output_dir)
    counts = Counter(str(e.get("kind")) for e in entries if e.get("kind"))
    latest_by_kind: dict[str, dict[str, Any]] = {}
    source_artifacts: list[str] = []
    for entry in entries:
        kind = entry.get("kind")
        if isinstance(kind, str):
            latest_by_kind[kind] = entry
        for artifact in entry.get("source_artifacts") or []:
            if isinstance(artifact, str) and artifact not in source_artifacts:
                source_artifacts.append(artifact)

    index = MemoryIndex(
        counts_by_kind=dict(counts),
        last_event=entries[-1] if entries else None,
        latest_by_kind=latest_by_kind,
        source_artifacts=source_artifacts,
    )
    path = _memory_index_path(output_dir)
    path.write_text(json.dumps(index.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_memory_index(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return MemoryIndex.model_validate(data).model_dump(mode="python")


def query_memory_entries_for_goal(
    output_dir: Path, goal_type: str, *, limit: int = 30
) -> list[dict[str, Any]]:
    """Return recent memory lines whose tags or payload reference *goal_type*."""
    entries = _read_entries(output_dir)
    gt = goal_type.strip().lower()
    matched: list[dict[str, Any]] = []
    for e in reversed(entries):
        if len(matched) >= limit:
            break
        tags = [str(t).lower() for t in (e.get("tags") or [])]
        if gt in tags:
            matched.append(e)
            continue
        payload = e.get("payload")
        if isinstance(payload, dict) and str(payload.get("goal_type", "")).lower() == gt:
            matched.append(e)
    return list(reversed(matched))


def format_recent_memory_for_brain_prompt(
    output_dir: Path,
    *,
    max_chars: int,
    limit_entries: int = 48,
) -> str:
    """Last *limit_entries* lines from JSONL, compact list for Gemini context (may be empty)."""

    if max_chars <= 0:
        return ""
    entries = _read_entries(output_dir)
    if not entries:
        return ""
    chunk = entries[-limit_entries:]
    lines: list[str] = []
    for e in chunk:
        kind = str(e.get("kind") or "")
        ts = str(e.get("ts") or "")[:32]
        summary = str(e.get("summary") or "").replace("\n", " ").strip()[:420]
        mem_id = str(e.get("memory_id") or "")[:12]
        tags = e.get("tags")
        tag_s = ""
        if isinstance(tags, list) and tags:
            tag_s = " [" + ",".join(str(t) for t in tags[:6]) + "]"
        lines.append(f"- {mem_id} {ts} {kind}{tag_s}: {summary}")
    body = "\n".join(lines)
    if len(body) > max_chars:
        body = body[:max_chars] + "\n[…truncado]"
    return body


def compact_memory_dry_run(output_dir: Path) -> dict[str, Any]:
    """Placeholder compaction report (does not delete or rewrite JSONL)."""
    entries = _read_entries(output_dir)
    return {
        "dry_run": True,
        "entries_total": len(entries),
        "would_merge_groups": 0,
        "note": "No destructive merge in V1; use for planning only.",
    }


def append_memory_from_json_artifact(
    output_dir: Path,
    *,
    kind: MemoryKind,
    artifact_relpath: str,
    summary: str,
    tags: list[str] | None = None,
    confidence: float = 0.7,
    mission_id: str | None = None,
    run_id: str | None = None,
) -> Path | None:
    """Append memory reading payload from an existing JSON artifact if present."""
    artifact_path = output_dir / artifact_relpath
    if not artifact_path.is_file():
        return None
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        payload = {"value": payload}
    return append_research_memory(
        output_dir,
        kind=kind,
        summary=summary,
        source_artifacts=[artifact_relpath],
        payload=payload,
        tags=tags,
        confidence=confidence,
        mission_id=mission_id,
        run_id=run_id,
    )

