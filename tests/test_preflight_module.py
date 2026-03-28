"""Preflight checks."""

from __future__ import annotations

import os

from paper_pipeline.pipeline.preflight import run_preflight, write_preflight_report


def test_preflight_ok_with_token(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "x")
    r = run_preflight(output_dir=tmp_path / "o", dry_run=False)
    assert r.ok
    p = write_preflight_report(tmp_path / "o", r)
    assert p.is_file()


def test_preflight_fails_without_token(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("PERPLEXITY_SESSION_TOKEN", raising=False)
    r = run_preflight(output_dir=tmp_path / "o", dry_run=False)
    assert not r.ok
