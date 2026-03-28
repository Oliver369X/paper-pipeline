"""Research / code packs only when eligible + flag."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from paper_pipeline.mission import Mission
from paper_pipeline.publication.publish_manager import write_publish_decision


def _mission(out: Path) -> Mission:
    return Mission(
        topic="t",
        paper_target="p",
        sections_needed=["gaps"],
        output_dir=str(out),
        mission_version=1,
        enable_quality_check=True,
    )


def test_no_packs_without_flag_even_if_eligible(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PAPER_PIPELINE_BUILD_PACKS", raising=False)
    out = tmp_path / "out"
    out.mkdir(parents=True)
    (out / "validation").mkdir(parents=True)
    (out / "validation" / "quality_validation.json").write_text(
        json.dumps({"publishable": True, "blocking_reasons": []}),
        encoding="utf-8",
    )
    (out / "triage").mkdir(parents=True)
    (out / "triage" / "triage_report.json").write_text(
        json.dumps({"tier": 2, "label": "x"}),
        encoding="utf-8",
    )
    write_publish_decision(out, _mission(out))
    assert not (out / "research_pack").exists()


def test_packs_created_with_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_BUILD_PACKS", "1")
    out = tmp_path / "out"
    out.mkdir(parents=True)
    (out / "draft_paper.md").write_text("# D\n", encoding="utf-8")
    (out / "validation").mkdir(parents=True)
    (out / "validation" / "quality_validation.json").write_text(
        json.dumps({"publishable": True, "blocking_reasons": []}),
        encoding="utf-8",
    )
    (out / "triage").mkdir(parents=True)
    (out / "triage" / "triage_report.json").write_text(
        json.dumps({"tier": 2, "label": "x"}),
        encoding="utf-8",
    )
    (out / "evidence").mkdir(parents=True)
    (out / "evidence" / "claims.json").write_text("[]", encoding="utf-8")
    (out / "evidence" / "evidence_index.json").write_text("{}", encoding="utf-8")
    write_publish_decision(out, _mission(out))
    assert (out / "research_pack" / "draft_paper.md").is_file()
    assert (out / "code_pack" / "MANIFEST.md").is_file()
