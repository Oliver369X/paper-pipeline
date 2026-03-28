"""Light replay: run.log JSONL lines can be parsed; ledger phases structure."""

from __future__ import annotations

import json
from pathlib import Path


def test_run_log_lines_are_json_objects(tmp_path: Path) -> None:
    log = tmp_path / "run.log"
    log.write_text(
        json.dumps({"step": "a", "ok": True}) + "\n"
        + json.dumps({"step": "b", "ok": True}) + "\n",
        encoding="utf-8",
    )
    phases: list[str] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if isinstance(row, dict) and "step" in row:
            phases.append(str(row["step"]))
    assert phases == ["a", "b"]


def test_ledger_phases_roundtrip_minimal(tmp_path: Path) -> None:
    from paper_pipeline.ledger.models import RunLedger

    out = tmp_path / "run_ledger.json"
    ledger = RunLedger.new_run(
        run_id="r1",
        mission_id="m",
        mission_version=1,
        phase_names=["preflight", "done"],
    )
    out.write_text(
        json.dumps(ledger.model_dump(mode="python"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data["phases"]) >= 2
    assert data["phases"][0]["name"] == "preflight"
