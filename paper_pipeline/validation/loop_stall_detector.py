"""Detect lack of progress between loop iterations."""

from __future__ import annotations


def is_stalled(previous_draft: str, new_draft: str, *, min_delta_chars: int = 20) -> bool:
    """Return True if the draft did not change meaningfully."""

    a = previous_draft.strip()
    b = new_draft.strip()
    if a == b:
        return True
    return abs(len(b) - len(a)) < min_delta_chars and a[:200] == b[:200]
