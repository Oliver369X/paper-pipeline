"""Append triage / breakthrough events to Notion via the official API.

Uses the same ``NOTION_TOKEN`` (internal integration) as the rest of the
pipeline and as configured for the **Notion MCP** in Cursor: one token, two
surfaces (REST from Python, MCP from the IDE).

Environment:
  NOTION_TOKEN — required to post
  NOTION_TRIAGE_PAGE_ID — page UUID to append blocks to (create an empty page
    in Notion, share it with the integration, copy the ID from the URL)
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from paper_pipeline.mission import Mission
from paper_pipeline.notion_sync import append_section_to_page

logger = logging.getLogger(__name__)


def maybe_append_triage_breakthrough_to_notion(
    mission: Mission,
    *,
    tier: int,
    label: str,
    reason: str,
    detail: dict,
    metrics: dict,
    output_dir: Path,
) -> None:
    """If tier is 3 and credentials are set, append a section to the triage page."""
    if tier != 3:
        return
    token = os.environ.get("NOTION_TOKEN", "").strip()
    page_id = os.environ.get("NOTION_TRIAGE_PAGE_ID", "").strip()
    if not token or not page_id:
        return

    title = f"Breakthrough · {label}"
    body = (
        f"**Topic:** {mission.topic}\n\n"
        f"**Paper target:** {mission.paper_target}\n\n"
        f"**Reason:** {reason}\n\n"
        f"**Output dir:** `{output_dir.resolve()}`\n\n"
        f"**Detail:**\n```json\n{json.dumps(detail, indent=2, ensure_ascii=False)}\n```\n\n"
        f"**Metrics:**\n```json\n{json.dumps(metrics, indent=2, ensure_ascii=False)}\n```\n"
    )
    try:
        append_section_to_page(token, page_id, title, body)
        logger.info("Notion triage section appended to page %s…", page_id[:8])
    except (OSError, RuntimeError) as exc:
        logger.warning("Notion triage append failed: %s", exc)
