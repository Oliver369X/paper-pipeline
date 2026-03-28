"""Integrity checks for the eval runner (sandbox isolation, future tampering)."""

from __future__ import annotations

from pathlib import Path


def verify_output_under_root(output_dir: Path, allowed_root: Path) -> bool:
    """Return True if *output_dir* is *allowed_root* or a subdirectory (resolved paths)."""
    try:
        output_dir.resolve().relative_to(allowed_root.resolve())
        return True
    except ValueError:
        return False


def tampering_placeholder_detected() -> bool:
    """Reserved for future checks (evaluator file access). Always False in V1."""
    return False
