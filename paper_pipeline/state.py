"""Persistent run state for resumable `paper-pipeline` runs."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_NAME = "run_state.json"


@dataclass
class RunState:
    """Tracks completed steps so a failed run can resume without redoing sections."""

    last_run: str = ""
    completed_steps: list[str] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    draft_version: int = 0
    draft_hash: str | None = None
    meta_loop_cycles: int = 0
    #: Persisted when ``Mission.single_thread_perplexity`` so runs can resume the same thread.
    perplexity_backend_uuid: str | None = None
    perplexity_read_write_token: str | None = None
    #: Último fallo crítico (experimento / CLI) para diagnóstico; no usado para resume.
    last_critical_failure: str = ""
    #: Huella del último ``metrics.json`` coherente (tier/fallback/profile); invalida resume si cambia.
    empirical_fingerprint: str = ""
    #: Hash de ``mission.experiment_runner`` del último run con experimento habilitado.
    experiment_runner_config_hash: str = ""

    @classmethod
    def load(cls, path: Path) -> RunState:
        if os.environ.get("PAPER_PIPELINE_DISABLE_RESUME", "").lower() in ("1", "true", "yes"):
            return cls()
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return cls(
                        last_run=str(data.get("last_run", "")),
                        completed_steps=list(data.get("completed_steps", [])),
                        pending_steps=list(data.get("pending_steps", [])),
                        errors=list(data.get("errors", [])),
                        draft_version=int(data.get("draft_version", 0)),
                        draft_hash=data.get("draft_hash"),
                        meta_loop_cycles=int(data.get("meta_loop_cycles", 0)),
                        perplexity_backend_uuid=data.get("perplexity_backend_uuid"),
                        perplexity_read_write_token=data.get("perplexity_read_write_token"),
                        last_critical_failure=str(data.get("last_critical_failure", "")),
                        empirical_fingerprint=str(data.get("empirical_fingerprint", "")),
                        experiment_runner_config_hash=str(data.get("experiment_runner_config_hash", "")),
                    )
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        return cls()

    def save(self, path: Path) -> None:
        self.last_run = datetime.now(UTC).isoformat()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(self), indent=2, ensure_ascii=False)
        fd, tmp = tempfile.mkstemp(
            dir=str(path.parent),
            prefix=".run_state_",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)
            os.replace(tmp, path)
        except OSError:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def mark_done(self, step: str) -> None:
        if step not in self.completed_steps:
            self.completed_steps.append(step)
        if step in self.pending_steps:
            self.pending_steps.remove(step)

    def already_done(self, step: str) -> bool:
        return step in self.completed_steps


def state_path_for(output_dir: Path) -> Path:
    return output_dir / STATE_NAME
