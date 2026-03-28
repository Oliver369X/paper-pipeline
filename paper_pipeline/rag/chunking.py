"""Split long text into chunks for embedding."""

from __future__ import annotations

import re


def chunk_text(text: str, *, max_chars: int) -> list[str]:
    """Split *text* into chunks of at most *max_chars*, preferring paragraph boundaries."""

    if max_chars <= 0:
        return []
    t = text.strip()
    if not t:
        return []
    if len(t) <= max_chars:
        return [t]

    paras = re.split(r"\n\s*\n+", t)
    chunks: list[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        s = buf.strip()
        if s:
            chunks.append(s)
        buf = ""

    for p in paras:
        p = p.strip()
        if not p:
            continue
        if len(p) > max_chars:
            flush()
            for i in range(0, len(p), max_chars):
                piece = p[i : i + max_chars].strip()
                if piece:
                    chunks.append(piece)
            continue
        if len(buf) + len(p) + 2 > max_chars and buf:
            flush()
        buf = f"{buf}\n\n{p}" if buf else p

    flush()
    return chunks
