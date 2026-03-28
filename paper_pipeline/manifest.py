"""Pipeline phase manifest persisted to ``outputs/manifest.json``."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

PhaseStatus = Literal["pending", "running", "done", "failed", "skipped"]


@dataclass
class PipelinePhase:
    name: str
    status: PhaseStatus = "pending"
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None


@dataclass
class PipelineManifest:
    """Ordered list of phases with status (for UI / resume hints)."""

    phases: list[PipelinePhase] = field(default_factory=list)
    updated_at: str = ""

    def to_json_dict(self) -> dict:
        return {
            "phases": [asdict(p) for p in self.phases],
            "updated_at": self.updated_at,
        }

    def write(self, output_dir: Path) -> Path:
        self.updated_at = datetime.now(UTC).isoformat()
        p = output_dir / "manifest.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_json_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return p

    def upsert_phase(
        self,
        name: str,
        status: PhaseStatus,
        *,
        error: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        for ph in self.phases:
            if ph.name == name:
                if status == "running" and ph.started_at is None:
                    ph.started_at = now
                ph.status = status
                if status in ("done", "failed", "skipped"):
                    ph.finished_at = now
                if error is not None:
                    ph.error = error
                return
        ph = PipelinePhase(name=name, status=status)
        ph.started_at = now if status == "running" else None
        if status in ("done", "failed", "skipped"):
            ph.finished_at = now
        if error is not None:
            ph.error = error
        self.phases.append(ph)


def default_pipeline_phases() -> list[str]:
    return [
        "perplexity_sections",
        "assembly_draft",
        "quality_check",
        "notion_sync",
        "cursor_cli",
    ]


def new_manifest(phase_names: list[str] | None = None) -> PipelineManifest:
    names = phase_names or default_pipeline_phases()
    return PipelineManifest(
        phases=[PipelinePhase(name=n, status="pending") for n in names],
    )
