"""Tests for markdown validators."""

from __future__ import annotations

from paper_pipeline.validators import validate_draft, validate_section


def test_section_minimum_length() -> None:
    result = validate_section("Hola", min_chars=300)
    assert not result.ok
    assert "short" in result.reason.lower()


def test_section_html_login() -> None:
    html_content = "<!DOCTYPE html><html><body>Please sign in</body></html>"
    result = validate_section(html_content, min_chars=10)
    assert not result.ok
    assert "html" in result.reason.lower()


def test_draft_no_duplicate_h2() -> None:
    draft = "## Intro\n\nA\n\n## Intro\n\nB"
    result = validate_draft(draft)
    assert not result.ok
    assert "duplicate" in result.reason.lower()


def test_draft_expected_sections_ok() -> None:
    draft = "## Intro\n\nx\n\n## Conclusion\n\ny"
    result = validate_draft(draft, expected_sections=["intro", "conclusion"])
    assert result.ok


def test_draft_missing_section() -> None:
    draft = "## Intro\n\nx"
    result = validate_draft(draft, expected_sections=["intro", "methodology"])
    assert not result.ok
    assert "methodology" in result.reason.lower() or "missing" in result.reason.lower()
