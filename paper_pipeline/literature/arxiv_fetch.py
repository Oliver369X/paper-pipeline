"""Fetch literature metadata from arXiv API."""

from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission

logger = logging.getLogger(__name__)

_ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5})", re.IGNORECASE)
_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def extract_arxiv_ids(text: str) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for m in _ARXIV_ID.finditer(text):
        aid = m.group(1)
        if aid not in seen:
            seen.add(aid)
            ids.append(aid)
    return ids


def fetch_arxiv_metadata(arxiv_id: str, *, timeout: float = 30.0) -> dict[str, Any] | None:
    query = f"id:{arxiv_id}"
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": query, "max_results": 1}
    )
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except Exception as exc:
        logger.warning("arXiv fetch failed for %s: %s", arxiv_id, exc)
        return None

    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None

    entry = root.find("atom:entry", _ATOM_NS)
    if entry is None:
        return None

    title_el = entry.find("atom:title", _ATOM_NS)
    summary_el = entry.find("atom:summary", _ATOM_NS)
    id_el = entry.find("atom:id", _ATOM_NS)
    authors = [
        a.find("atom:name", _ATOM_NS).text
        for a in entry.findall("atom:author", _ATOM_NS)
        if a.find("atom:name", _ATOM_NS) is not None
    ]
    return {
        "arxiv_id": arxiv_id,
        "title": (title_el.text or "").strip() if title_el is not None else "",
        "abstract": (summary_el.text or "").strip() if summary_el is not None else "",
        "url": (id_el.text or "").strip() if id_el is not None else f"https://arxiv.org/abs/{arxiv_id}",
        "authors": authors[:10],
    }


def run_literature_ingest_phase(
    mission: Mission,
    out: Path,
    plog: PipelineLogger,
    *,
    manifest: PipelineManifest | None,
) -> None:
    """Write ``outputs/literature/ingested.json`` when arXiv IDs are found."""

    lit_dir = out / "literature"
    lit_dir.mkdir(parents=True, exist_ok=True)
    out_path = lit_dir / "ingested.json"

    if manifest:
        manifest.upsert_phase("literature_ingest", "running")

    ids = extract_arxiv_ids(f"{mission.topic} {mission.paper_target}")
    papers: list[dict[str, Any]] = []
    for aid in ids[:5]:
        meta = fetch_arxiv_metadata(aid)
        if meta:
            papers.append(meta)

    payload = {
        "schema_version": 1,
        "arxiv_ids_requested": ids,
        "papers": papers,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    plog.step_ok("step:literature_ingest", papers=len(papers))
    if manifest:
        manifest.upsert_phase("literature_ingest", "done")
        manifest.write(out)
