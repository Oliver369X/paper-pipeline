"""Atomic-ish writes for ``run_ledger.json``."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from paper_pipeline.ledger.models import LedgerDecision, LedgerIntegrations, LedgerPhase, RunLedger

PhaseStatus = Literal["pending", "running", "done", "failed", "skipped"]


class LedgerWriter:
    LEDGER_NAME = "run_ledger.json"

    def __init__(self, output_dir: Path, *, mission_path: Path | None = None) -> None:
        self.output_dir = output_dir
        self.mission_path = mission_path
        self._path = output_dir / self.LEDGER_NAME
        self._ledger: RunLedger | None = None

    @property
    def path(self) -> Path:
        return self._path

    def start(
        self,
        *,
        mission_id: str,
        mission_version: int,
        phase_names: list[str],
        run_id: str | None = None,
    ) -> RunLedger:
        rid = run_id or f"{datetime.now(UTC).strftime('%Y-%m-%dT%H-%M-%SZ')}__{uuid.uuid4().hex[:8]}"
        self._ledger = RunLedger.new_run(
            run_id=rid,
            mission_id=mission_id,
            mission_version=mission_version,
            phase_names=phase_names,
        )
        if self.mission_path is not None:
            self._ledger.meta["mission_path"] = str(self.mission_path.resolve())
        self._write()
        return self._ledger

    def _write(self) -> None:
        if self._ledger is None:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._ledger.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def upsert_phase(
        self,
        name: str,
        status: PhaseStatus,
        *,
        artifacts: list[str] | None = None,
        error: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        if self._ledger is None:
            return
        now = datetime.now(UTC).isoformat()
        found = False
        for ph in self._ledger.phases:
            if ph.name == name:
                found = True
                if status == "running" and ph.started_at is None:
                    ph.started_at = now
                ph.status = status
                if status in ("done", "failed", "skipped"):
                    ph.ended_at = now
                if artifacts is not None:
                    ph.artifacts = artifacts
                if error is not None:
                    ph.error = error
                if meta:
                    ph.meta.update(meta)
                break
        if not found:
            ph = LedgerPhase(name=name, status=status, started_at=now if status == "running" else None)
            if status in ("done", "failed", "skipped"):
                ph.ended_at = now
            if artifacts is not None:
                ph.artifacts = artifacts
            if error is not None:
                ph.error = error
            if meta:
                ph.meta.update(meta)
            self._ledger.phases.append(ph)

        self._ledger.current_phase = name
        self._write()

    def set_integrations(self, **kwargs: Any) -> None:
        if self._ledger is None:
            return
        for k, v in kwargs.items():
            if hasattr(self._ledger.integrations, k):
                setattr(self._ledger.integrations, k, v)
        self._write()

    def set_decision(self, decision: LedgerDecision) -> None:
        if self._ledger is None:
            return
        self._ledger.decision = decision
        self._write()

    def finalize(self, status: Literal["completed", "failed", "cancelled"]) -> None:
        if self._ledger is None:
            return
        self._ledger.status = status
        self._ledger.ended_at = datetime.now(UTC).isoformat()
        self._ledger.current_phase = None
        self._write()

    @property
    def ledger(self) -> RunLedger | None:
        return self._ledger

    def load_existing(self) -> RunLedger | None:
        if not self._path.is_file():
            return None
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._ledger = RunLedger.model_validate(data)
            return self._ledger
        except (json.JSONDecodeError, OSError, ValueError):
            return None


def merge_ledger_after_triage(output_dir: Path) -> bool:
    """Sync ``run_ledger.json`` ``decision`` from ``publish_decision.json`` + triage tier."""

    w = LedgerWriter(output_dir)
    if w.load_existing() is None:
        return False
    pub_path = output_dir / "publication" / "publish_decision.json"
    tier: int | None = None
    tr_path = output_dir / "triage" / "triage_report.json"
    if tr_path.is_file():
        try:
            data = json.loads(tr_path.read_text(encoding="utf-8"))
            t = data.get("tier")
            tier = int(t) if t is not None else None
        except (json.JSONDecodeError, TypeError, ValueError, OSError):
            pass
    publishable = False
    blocking: list[str] = []
    if pub_path.is_file():
        try:
            p = json.loads(pub_path.read_text(encoding="utf-8"))
            publishable = bool(p.get("eligible_for_publication"))
            blocking = list(p.get("blocking_reasons") or [])
        except (json.JSONDecodeError, OSError):
            pass
    w.set_decision(
        LedgerDecision(
            triage_tier=tier,
            publishable=publishable,
            blocking_reasons=blocking,
        ),
    )
    return True
