"""Append section content to a Notion page (official API, internal integration)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


NOTION_VERSION = "2022-06-28"
MAX_TEXT = 1800


@dataclass(frozen=True)
class SyncSectionsResult:
    """Result of :func:`sync_sections` (partial failures do not raise)."""

    ok: bool
    """True if every existing section file synced without error."""
    errors: list[str] = field(default_factory=list)
    """Human-readable failure messages per section."""
    skipped_missing: list[str] = field(default_factory=list)
    """Section titles skipped because the file was missing."""


def normalize_notion_page_or_block_id(raw: str) -> str:
    """Return a UUID string for API paths (accepts URL paste, 32 hex, or dashed UUID).

    En URLs de Notion, el id suele ser los **últimos 32 caracteres hex** del último segmento
    del path (tras el título de la página).
    """

    s = raw.strip()
    if not s:
        return s
    if "?" in s:
        s = s.split("?", 1)[0].strip()
    s = s.rstrip("/")
    m = re.search(
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        s,
        re.I,
    )
    if m:
        return m.group(1).lower()
    # Slug Notion: .../Nombre-página-<32hex>
    last_seg = s.split("/")[-1]
    hex_tail = re.sub(r"[^0-9a-fA-F]", "", last_seg)
    if len(hex_tail) >= 32:
        h = hex_tail[-32:].lower()
        return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
    # UUID plano sin URL
    hex_only = re.sub(r"[^0-9a-fA-F]", "", s)
    if len(hex_only) == 32:
        h = hex_only.lower()
        return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
    return s


def verify_notion_token(token: str) -> dict[str, object]:
    """GET ``/v1/users/me`` — confirms the integration token works (no page ID required)."""

    url = "https://api.notion.com/v1/users/me"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if resp.status != 200:
                raise RuntimeError(f"Notion API error {resp.status}: {raw}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API HTTP {exc.code}: {body}") from exc
    data = json.loads(raw)
    if data.get("object") != "user":
        raise RuntimeError(f"Unexpected Notion users/me payload: {raw[:500]}")
    return data


def _chunk_text(text: str) -> list[str]:
    """Split into Notion-safe chunks (rich text content limit)."""

    text = text.strip()
    if not text:
        return [""]
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + MAX_TEXT])
        i += MAX_TEXT
    return chunks


def _paragraph_block(text: str) -> dict[str, object]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text[:2000]},
                }
            ]
        },
    }


def _heading_block(title: str) -> dict[str, object]:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": title[:2000]},
                }
            ]
        },
    }


def append_section_to_page(
    token: str,
    page_id: str,
    section_title: str,
    markdown_body: str,
) -> None:
    """Append a heading and paragraph blocks to the given page or block."""

    page_id = normalize_notion_page_or_block_id(page_id)
    if not re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        page_id,
        re.I,
    ):
        raise ValueError(
            "notion_page_id debe ser un UUID de página o bloque (32 hex o con guiones). "
            "Podés pegar la URL de la página: se extrae el id automáticamente.",
        )
    # En el path, Notion exige el id en 32 hex sin guiones (con guiones devuelve 400 validation_error).
    block_id_path = page_id.replace("-", "")
    url = f"https://api.notion.com/v1/blocks/{block_id_path}/children"
    children: list[dict[str, object]] = [_heading_block(section_title)]
    for chunk in _chunk_text(markdown_body):
        children.append(_paragraph_block(chunk))

    # Notion allows max 100 children per request
    for i in range(0, len(children), 100):
        batch = children[i : i + 100]
        body = json.dumps({"children": batch}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="PATCH",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                if resp.status not in (200, 201):
                    raw = resp.read().decode("utf-8", errors="replace")
                    msg = f"Notion API error {resp.status}: {raw}"
                    raise RuntimeError(msg)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            msg = f"Notion API HTTP {exc.code}: {body}"
            if exc.code == 404 and "object_not_found" in body:
                msg += (
                    "\n(En Notion: abrí la página → ··· arriba a la derecha → "
                    "«Conexiones» / «Connections» → añadí la integración del pipeline.)"
                )
            raise RuntimeError(msg) from exc


def sync_sections(
    token: str,
    page_id: str,
    section_files: list[tuple[str, Path]],
    log_path: Path,
) -> SyncSectionsResult:
    """Append each section file to Notion and append lines to log_path.

    Returns a :class:`SyncSectionsResult` (no exception for per-section HTTP failures).
    """

    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        f"# notion_sync {datetime.now(UTC).isoformat()} UTC",
        "",
    ]
    errors: list[str] = []
    skipped: list[str] = []
    for title, path in section_files:
        if not path.is_file():
            lines.append(f"SKIP (missing): {title} -> {path}")
            skipped.append(title)
            continue
        body = path.read_text(encoding="utf-8")
        try:
            append_section_to_page(token, page_id, title, body)
            lines.append(f"OK: {title} ({len(body)} chars)")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, RuntimeError) as exc:
            msg = f"{title}: {exc!s}"
            lines.append(f"FAIL: {title}: {exc!s}")
            errors.append(msg)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return SyncSectionsResult(ok=len(errors) == 0, errors=errors, skipped_missing=skipped)
