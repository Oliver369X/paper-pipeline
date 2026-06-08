"""Extract and curate sources from section markdown files."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from paper_pipeline.integrations.mistral_client import MistralClient
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest
from paper_pipeline.mission import Mission
from paper_pipeline.pipeline.common import OPENAI_COMPAT_PROVIDERS

logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"https?://[^\s\)\]>\"']+", re.IGNORECASE)
_ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})", re.IGNORECASE)
_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\)\]>\"']+", re.IGNORECASE)
_JSON_BLOCK = re.compile(r"\[[\s\S]*\]", re.MULTILINE)


def extract_urls_from_text(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for m in _URL_RE.finditer(text):
        url = m.group(0).rstrip(".,;")
        if url not in seen:
            seen.add(url)
            found.append(url)
    for m in _ARXIV_RE.finditer(text):
        aid = f"https://arxiv.org/abs/{m.group(1)}"
        if aid not in seen:
            seen.add(aid)
            found.append(aid)
    for m in _DOI_RE.finditer(text):
        doi = f"https://doi.org/{m.group(0)}"
        if doi not in seen:
            seen.add(doi)
            found.append(doi)
    return found


def _heuristic_score(url: str, topic: str) -> float:
    blob = (url + " " + topic).lower()
    score = 0.5
    if "arxiv" in url or "doi.org" in url or "semanticscholar" in url:
        score += 0.2
    if any(w in blob for w in topic.lower().split()[:5]):
        score += 0.1
    return min(1.0, score)


def _parse_curation_scores(raw: str, urls: list[str]) -> dict[str, float]:
    raw = raw.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            out: dict[str, float] = {}
            for item in data:
                if isinstance(item, dict) and "url" in item and "score" in item:
                    try:
                        out[str(item["url"])] = float(item["score"])
                    except (TypeError, ValueError):
                        continue
            return out
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK.search(raw)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return _parse_curation_scores(json.dumps(data), urls)
        except json.JSONDecodeError:
            pass
    return {u: _heuristic_score(u, "") for u in urls}


def run_source_curation_phase(
    mission: Mission,
    out: Path,
    written: list[tuple[str, Path]],
    plog: PipelineLogger,
    *,
    manifest: PipelineManifest | None,
    mistral_client: MistralClient | None = None,
    max_results: int = 10,
) -> None:
    """Write ``outputs/sources_curated.json`` (best-effort, non-blocking)."""

    if manifest:
        manifest.upsert_phase("source_curation", "running")

    all_urls: list[str] = []
    by_section: dict[str, list[str]] = {}
    for section, path in written:
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        if section in ("draft_paper", "quality_gaps", "code/README"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        urls = extract_urls_from_text(text)
        by_section[section] = urls
        all_urls.extend(urls)

    deduped: list[str] = []
    seen: set[str] = set()
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    if not deduped:
        payload: dict[str, Any] = {
            "schema_version": 1,
            "status": "no_urls",
            "sources": [],
            "by_section": by_section,
        }
        (out / "sources_curated.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        plog.step_ok("step:source_curation", status="no_urls")
        if manifest:
            manifest.upsert_phase("source_curation", "done")
            manifest.write(out)
        return

    scores: dict[str, float] = {}
    if mission.provider in OPENAI_COMPAT_PROVIDERS and mistral_client is not None and mission.provider == "mistral":
        url_blob = "\n".join(f"- {u}" for u in deduped[:30])
        prompt = (
            f"Topic: {mission.topic}\n"
            f"Score each URL 0.0-1.0 for relevance to the topic.\n"
            f"Return JSON array: [{{\"url\": \"...\", \"score\": 0.9, \"reason\": \"...\"}}]\n\n"
            f"URLs:\n{url_blob}"
        )
        try:
            raw = mistral_client.ask_single(prompt, temperature=0.1)
            scores = _parse_curation_scores(raw, deduped)
        except Exception as exc:
            logger.warning("Mistral curation failed, using heuristics: %s", exc)

    sources: list[dict[str, Any]] = []
    for url in deduped:
        score = scores.get(url, _heuristic_score(url, mission.topic))
        sources.append({"url": url, "score": round(score, 3)})

    sources.sort(key=lambda x: x["score"], reverse=True)
    sources = sources[:max_results]

    payload = {
        "schema_version": 1,
        "status": "ok",
        "topic": mission.topic,
        "sources": sources,
        "by_section": by_section,
    }
    (out / "sources_curated.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    plog.step_ok("step:source_curation", count=len(sources))
    if manifest:
        manifest.upsert_phase("source_curation", "done")
        manifest.write(out)
