"""Unit tests for Notion ID normalization (no network)."""

from __future__ import annotations

from paper_pipeline.notion_sync import normalize_notion_page_or_block_id


def test_normalize_dashed_uuid_unchanged() -> None:
    pid = "67e44513-9800-8039-4513-068498300920"
    assert normalize_notion_page_or_block_id(pid) == pid.lower()


def test_normalize_32_hex_to_dashed() -> None:
    h = "67e44513980080394513068498300920"
    out = normalize_notion_page_or_block_id(h)
    assert out.replace("-", "") == h.lower()


def test_normalize_from_notion_url() -> None:
    url = "https://www.notion.so/My-Page-67e44513980080394513068498300920?v=1"
    out = normalize_notion_page_or_block_id(url)
    assert out.replace("-", "") == "67e44513980080394513068498300920"
