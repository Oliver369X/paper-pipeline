"""Global citation index for assembled drafts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BRACKET_CITE = re.compile(r"\[(\d+)\]")
_URL_INLINE = re.compile(r"https?://[^\s\)\]>\"']+", re.IGNORECASE)


@dataclass
class CitationEntry:
    id: int
    url: str
    section: str
    raw_marker: str


def _collect_from_section(section: str, text: str) -> tuple[list[CitationEntry], str]:
    entries: list[CitationEntry] = []
    url_to_id: dict[str, int] = {}
    next_id = 1

    def assign(url: str, marker: str) -> int:
        nonlocal next_id
        if url in url_to_id:
            return url_to_id[url]
        cid = next_id
        next_id += 1
        url_to_id[url] = cid
        entries.append(CitationEntry(id=cid, url=url, section=section, raw_marker=marker))
        return cid

    rewritten = text
    for url in _URL_INLINE.findall(text):
        clean = url.rstrip(".,;")
        assign(clean, url)

    def renum_bracket(match: re.Match[str]) -> str:
        num = int(match.group(1))
        return f"[{num}]"

    rewritten = _BRACKET_CITE.sub(renum_bracket, rewritten)
    return entries, rewritten


def build_citation_index(
    written: list[tuple[str, Path]],
) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (index_json, section_text_rewrites)."""

    global_map: dict[str, int] = {}
    all_entries: list[CitationEntry] = []
    rewrites: dict[str, str] = {}
    next_global = 1

    for section, path in written:
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        if section.startswith("code/") or section in ("draft_paper", "quality_gaps"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        local_entries, _ = _collect_from_section(section, text)
        new_lines: list[str] = []
        for line in text.splitlines():
            new_line = line
            for url in _URL_INLINE.findall(line):
                clean = url.rstrip(".,;")
                if clean not in global_map:
                    global_map[clean] = next_global
                    all_entries.append(
                        CitationEntry(
                            id=next_global,
                            url=clean,
                            section=section,
                            raw_marker=url,
                        )
                    )
                    next_global += 1
                gid = global_map[clean]
                new_line = new_line.replace(url, f"[{gid}]")
            new_lines.append(new_line)
        rewrites[section] = "\n".join(new_lines) + ("\n" if text.endswith("\n") else "")

    index = {
        "schema_version": 1,
        "citations": [
            {"id": e.id, "url": e.url, "section": e.section, "raw_marker": e.raw_marker}
            for e in all_entries
        ],
    }
    return index, rewrites


def apply_citation_index_to_draft(
    draft_text: str,
    index: dict[str, Any],
) -> str:
    """Renumber bracket citations sequentially in final draft."""
    citations = index.get("citations")
    if not isinstance(citations, list):
        return draft_text
    url_by_id = {c["id"]: c["url"] for c in citations if isinstance(c, dict) and "id" in c and "url" in c}
    lines = []
    for line in draft_text.splitlines():
        for cid, url in url_by_id.items():
            if url in line:
                line = line.replace(url, f"[{cid}]")
        lines.append(line)
    return "\n".join(lines) + ("\n" if draft_text.endswith("\n") else "")


def write_citation_index(output_dir: Path, index: dict[str, Any]) -> Path:
    p = output_dir / "citation_index.json"
    p.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
