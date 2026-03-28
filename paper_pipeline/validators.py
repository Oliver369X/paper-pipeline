"""Lightweight validation of generated markdown (no strict guarantees)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    reason: str = ""


_HTML_HINT = re.compile(r"<\s*!DOCTYPE\s+html|<\s*html[\s>]", re.IGNORECASE)
_H2 = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def validate_section(content: str, *, min_chars: int = 300) -> ValidationResult:
    """Heuristic checks on a single section body."""
    text = (content or "").strip()
    if len(text) < min_chars:
        return ValidationResult(False, f"too short ({len(text)} chars, min {min_chars})")
    if _HTML_HINT.search(text):
        return ValidationResult(False, "looks like HTML (possible auth/login page)")
    return ValidationResult(True, "")


def validate_draft(
    draft: str,
    *,
    expected_sections: list[str] | None = None,
) -> ValidationResult:
    """Check duplicate H2 titles and optional presence of section slugs."""
    text = draft or ""
    headers = _H2.findall(text)
    lowered = [h.strip().lower() for h in headers]
    if len(lowered) != len(set(lowered)):
        return ValidationResult(False, "duplicate H2 headings detected")
    if expected_sections:
        blob = text.lower()
        missing = [s for s in expected_sections if s.lower() not in blob]
        if missing:
            return ValidationResult(False, f"missing sections or headings: {', '.join(missing)}")
    return ValidationResult(True, "")
