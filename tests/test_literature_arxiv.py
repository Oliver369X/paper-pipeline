"""Tests for arXiv literature ingest."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from paper_pipeline.literature.arxiv_fetch import extract_arxiv_ids, fetch_arxiv_metadata
from paper_pipeline.mission import Mission
from paper_pipeline.literature.arxiv_fetch import run_literature_ingest_phase


def test_extract_arxiv_ids() -> None:
    ids = extract_arxiv_ids("See arXiv:2305.04091 and 2401.12345")
    assert "2305.04091" in ids
    assert "2401.12345" in ids


def test_fetch_arxiv_metadata_mock() -> None:
    xml = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title> Test Paper </title>
        <summary> Abstract here </summary>
        <id>http://arxiv.org/abs/2305.04091v1</id>
        <author><name>Alice</name></author>
      </entry>
    </feed>"""
    with patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = xml.encode("utf-8")
        meta = fetch_arxiv_metadata("2305.04091")
    assert meta is not None
    assert "Test Paper" in meta["title"]


def test_literature_ingest_writes_json(tmp_path: Path) -> None:
    mission = Mission(topic="x", paper_target="arxiv:2305.04091")
    plog = MagicMock()
    with patch(
        "paper_pipeline.literature.arxiv_fetch.fetch_arxiv_metadata",
        return_value={"arxiv_id": "2305.04091", "title": "T", "abstract": "A", "url": "u", "authors": []},
    ):
        run_literature_ingest_phase(mission, tmp_path, plog, manifest=None)
    p = tmp_path / "literature" / "ingested.json"
    assert p.is_file()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data["papers"]) >= 1
