"""Optional real Notion API checks — skipped unless env vars are set.

- ``NOTION_TOKEN`` only: ``test_notion_token_is_valid`` (GET ``/users/me``).
- ``NOTION_TOKEN`` + ``NOTION_SMOKE_PAGE_ID``: also appends a smoke block.

Run: ``pytest tests/test_notion_smoke_optional.py -m notion_real -v``
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.notion_real


@pytest.mark.skipif(
    not os.environ.get("NOTION_TOKEN", "").strip(),
    reason="Set NOTION_TOKEN to validate integration with Notion API",
)
def test_notion_token_is_valid() -> None:
    from paper_pipeline.notion_sync import verify_notion_token

    token = os.environ["NOTION_TOKEN"].strip()
    data = verify_notion_token(token)
    assert data.get("type") in ("bot", "person"), "expected bot or person user"


@pytest.mark.skipif(
    not os.environ.get("NOTION_TOKEN", "").strip()
    or not os.environ.get("NOTION_SMOKE_PAGE_ID", "").strip(),
    reason="Set NOTION_TOKEN and NOTION_SMOKE_PAGE_ID to run real Notion write",
)
def test_append_smoke_block_to_notion_page() -> None:
    from paper_pipeline.notion_sync import append_section_to_page

    token = os.environ["NOTION_TOKEN"].strip()
    page_id = os.environ["NOTION_SMOKE_PAGE_ID"].strip()
    try:
        append_section_to_page(
            token,
            page_id,
            "paper-pipeline smoke (pytest)",
            "Bloque de prueba automática. Podés borrar esta sección.",
        )
    except RuntimeError as exc:
        if "object_not_found" in str(exc) and "404" in str(exc):
            pytest.skip(
                "Notion 404: la página no existe para la integración o no está "
                "conectada (Notion → ··· → Conexiones → tu integración).",
            )
        raise
