"""Tests for PipelineLogger JSONL output."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.logger import PipelineLogger


def test_pipeline_logger_writes_json_lines(tmp_path: Path) -> None:
    pl = PipelineLogger(tmp_path)
    pl.step_start("test_step", foo=1)
    pl.step_ok("test_step", bar=2)
    log = tmp_path / "run.log"
    assert log.is_file()
    lines = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert lines[0]["event"] == "step_start"
    assert lines[0]["level"] == "info"
    assert lines[0]["module"] == "paper_pipeline.logger"
    assert lines[1]["event"] == "step_ok"
    assert "duration_s" in lines[1]
