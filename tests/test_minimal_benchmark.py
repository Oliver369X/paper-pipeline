"""Built-in experiment runner writes metrics.json (numpy or skipped)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.experiments.minimal_benchmark import run_minimal_benchmark


def test_run_minimal_benchmark_writes_json(tmp_path: Path) -> None:
    pytest.importorskip("numpy")
    out = run_minimal_benchmark(tmp_path)
    p = tmp_path / "metrics.json"
    assert p.is_file()
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert raw.get("schema_version") == 1
    assert (raw.get("experiment_runner") or {}).get("status") == "ok"
    assert raw.get("main") is not None
    assert isinstance(out, dict)
    assert out.get("experiment_runner", {}).get("status") == "ok"


def test_suggested_code_files_filter() -> None:
    from paper_pipeline.brain.service import suggested_code_files_from_raw

    raw = {
        "suggested_code_files": {
            "outputs/code/x.py": "print(1)",
            "outputs/evil.py": "bad",
            "../outputs/code/y.py": "bad",
        }
    }
    got = suggested_code_files_from_raw(raw)
    assert got == {"outputs/code/x.py": "print(1)"}
