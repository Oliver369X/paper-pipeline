"""Parser de directivas @PERPLEXITY / @NOTION / @CURSOR (sin mocks de red)."""

from __future__ import annotations

from paper_pipeline.loop_directives import (
    CursorDirective,
    NotionDirective,
    PerplexityDirective,
    parse_directives,
    strip_directive_blocks,
)


def test_parse_perplexity_with_body() -> None:
    text = """Some intro
@PERPLEXITY:gaps
line one
line two
@NOTION
"""
    d = parse_directives(text)
    assert len(d) == 2
    assert isinstance(d[0], PerplexityDirective)
    assert d[0].section == "gaps"
    assert "line one" in d[0].body
    assert isinstance(d[1], NotionDirective)


def test_parse_cursor_with_optional_body() -> None:
    text = """@CURSOR
Use only outputs/code
"""
    d = parse_directives(text)
    assert len(d) == 1
    assert isinstance(d[0], CursorDirective)
    assert "outputs/code" in d[0].body


def test_parse_utf8_bom_ignored() -> None:
    content = "\ufeff@PERPLEXITY:intro\nbody"
    d = parse_directives(content)
    assert len(d) == 1
    assert isinstance(d[0], PerplexityDirective)
    assert d[0].section == "intro"


def test_parse_perplexity_tag_case_insensitive() -> None:
    text = "@perplexity:gaps\n"
    d = parse_directives(text)
    assert len(d) == 1
    assert isinstance(d[0], PerplexityDirective)
    assert d[0].section == "gaps"


def test_strip_removes_blocks() -> None:
    text = """Keep this
@PERPLEXITY:sota
gone
@NOTION
Tail
"""
    out = strip_directive_blocks(text)
    assert "Keep" in out
    assert "gone" not in out
    assert "Tail" in out
