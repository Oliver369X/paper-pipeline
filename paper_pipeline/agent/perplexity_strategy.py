"""Perplexity Strategy Layer V1: profiles, fingerprints, call records (no scraper imports)."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

QueryMode = Literal["discovery", "verification", "synthesis", "review", "monitor"]
CostClass = Literal["low", "medium", "high"]

RECORD_NAME = "perplexity_call_record.jsonl"


class PerplexityProfile(BaseModel):
    """Named profile for a query regime."""

    id: str
    mode: QueryMode
    cost_class: CostClass
    web: bool = True


class ResolvedCallPlan(BaseModel):
    profile_id: str
    mode: QueryMode
    model: str
    cost_class: CostClass
    web: bool = True


def perplexity_strategy_enabled() -> bool:
    return os.environ.get("PAPER_PIPELINE_PERPLEXITY_STRATEGY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _infer_mode_from_section(section: str) -> QueryMode:
    s = section.lower()
    if any(k in s for k in ("related", "sota", "gap", "literature", "survey")):
        return "discovery"
    if any(k in s for k in ("method", "experiment", "ablation", "eval")):
        return "verification"
    if any(k in s for k in ("quality", "discussion", "conclusion", "limitation")):
        return "review"
    return "synthesis"


def _profile_for_mode(mode: QueryMode) -> PerplexityProfile:
    if mode == "discovery":
        return PerplexityProfile(id="deep_discovery", mode=mode, cost_class="high", web=True)
    if mode == "verification":
        return PerplexityProfile(id="fast_check", mode=mode, cost_class="medium", web=True)
    if mode == "review":
        return PerplexityProfile(id="review_mode", mode=mode, cost_class="medium", web=True)
    return PerplexityProfile(id="synthesis_profile", mode=mode, cost_class="low", web=False)


def resolve_profile_for_section(section: str, mission_model: str) -> ResolvedCallPlan:
    """Pick a profile from section name and mission model (no I/O)."""
    mode = _infer_mode_from_section(section)
    prof = _profile_for_mode(mode)
    model = mission_model.strip() or "best"
    return ResolvedCallPlan(
        profile_id=prof.id,
        mode=prof.mode,
        model=model,
        cost_class=prof.cost_class,
        web=prof.web,
    )


def query_fingerprint(prompt: str, scope: str) -> str:
    """Stable short hash for dedup/logging (normalized whitespace)."""
    norm = " ".join(prompt.split())
    raw = f"{scope}\n{norm}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


class CallRecord(BaseModel):
    ts: str
    query_hash: str
    profile_id: str
    mode: str
    model: str
    cost_class: str
    section_or_goal: str
    mission_id: str | None = None
    web: bool = True

    model_config = {"extra": "forbid"}


def append_call_record(
    output_dir: Path,
    record: CallRecord,
) -> Path:
    """Append one JSON line to ``outputs/perplexity_call_record.jsonl``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / RECORD_NAME
    line = json.dumps(record.model_dump(mode="python"), ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
    return path


def record_planned_call(
    output_dir: Path,
    *,
    prompt: str,
    section: str,
    mission_model: str,
    mission_id: str | None = None,
) -> Path | None:
    """If strategy enabled, record a planned Perplexity call; otherwise return None."""
    if not perplexity_strategy_enabled():
        return None
    plan = resolve_profile_for_section(section, mission_model)
    fp = query_fingerprint(prompt, section)
    rec = CallRecord(
        ts=datetime.now(UTC).isoformat(),
        query_hash=fp,
        profile_id=plan.profile_id,
        mode=plan.mode,
        model=plan.model,
        cost_class=plan.cost_class,
        section_or_goal=section,
        mission_id=mission_id,
        web=plan.web,
    )
    return append_call_record(output_dir, rec)
