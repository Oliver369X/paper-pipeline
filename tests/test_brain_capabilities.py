"""L1 brain catalog: load from disk, prompt includes anchors (no Gemini)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from paper_pipeline.brain import prompts as brain_prompts

# Actualizar cuando cambie paper_pipeline/brain/brain_capabilities.md (CI opcional).
_BRAIN_CAPABILITIES_SHA256 = "e00d92d1c70bc82e8be170e66d1348f8021db00dc13301f2d5e0852a95eccf95"


def test_load_brain_capabilities_not_empty() -> None:
    text = brain_prompts.load_brain_capabilities_text()
    assert len(text) > 400
    assert "Imposibilidades" in text
    assert "Gemini" in text


def test_build_brain_system_prompt_includes_l1() -> None:
    p = brain_prompts.build_brain_system_prompt()
    assert "Catálogo L1" in p or "Identidad del cerebro" in p
    assert "Imposibilidades" in p
    assert "reply" in p and "brief_markdown" in p
    assert "cursor_checklist_markdown" in p
    assert "run_pipeline" in p


def test_build_brain_variants_prompt_includes_l1() -> None:
    p = brain_prompts.build_brain_variants_system_prompt(3)
    assert "variants" in p
    assert "Imposibilidades" in p


def test_capabilities_file_exists_next_to_prompts() -> None:
    cap = Path(brain_prompts.__file__).resolve().parent / "brain_capabilities.md"
    assert cap.is_file()


def test_brain_capabilities_sha256_matches_pinned() -> None:
    """Regresión: el catálogo L1 no debe cambiar sin actualizar el hash esperado."""
    assert brain_prompts.brain_capabilities_sha256_hex() == _BRAIN_CAPABILITIES_SHA256
    p = Path(brain_prompts.__file__).resolve().parent / "brain_capabilities.md"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == _BRAIN_CAPABILITIES_SHA256
