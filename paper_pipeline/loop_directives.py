"""Parse @PERPLEXITY / @NOTION / @CURSOR blocks from cursor_turn.md or next_instruction.md."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PerplexityDirective:
    section: str
    body: str


@dataclass(frozen=True)
class NotionDirective:
    pass


@dataclass(frozen=True)
class CursorDirective:
    body: str


Directive = PerplexityDirective | NotionDirective | CursorDirective

_LINE_PPLX = re.compile(r"^@PERPLEXITY:([\w-]+)\s*$", re.IGNORECASE)
_LINE_NOTION = re.compile(r"^@NOTION\s*$", re.IGNORECASE)
_LINE_CURSOR = re.compile(r"^@CURSOR\s*$", re.IGNORECASE)


def parse_directives(text: str) -> list[Directive]:
    """Extract directives in order. Body for @PERPLEXITY runs until the next @ line or EOF."""

    if text.startswith("\ufeff"):
        text = text[1:]
    lines = text.splitlines()
    out: list[Directive] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        m = _LINE_PPLX.match(line)
        if m:
            section = m.group(1).strip()
            i += 1
            body_lines: list[str] = []
            while i < len(lines):
                nxt = lines[i].strip()
                if nxt.startswith("@"):
                    break
                body_lines.append(lines[i])
                i += 1
            out.append(PerplexityDirective(section=section, body="\n".join(body_lines).strip()))
            continue
        if _LINE_NOTION.match(line):
            out.append(NotionDirective())
            i += 1
            continue
        if _LINE_CURSOR.match(line):
            i += 1
            body_lines = []
            while i < len(lines):
                nxt = lines[i].strip()
                if nxt.startswith("@"):
                    break
                body_lines.append(lines[i])
                i += 1
            out.append(CursorDirective(body="\n".join(body_lines).strip()))
            continue
        i += 1
    return out


def strip_directive_blocks(text: str) -> str:
    """Remove all directive blocks (same grammar as parse) for re-saving after execution."""

    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if _LINE_PPLX.match(line):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("@"):
                i += 1
            continue
        if _LINE_NOTION.match(line):
            i += 1
            continue
        if _LINE_CURSOR.match(line):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("@"):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out).strip() + ("\n" if out else "")
