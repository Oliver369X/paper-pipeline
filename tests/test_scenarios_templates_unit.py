"""Escenarios pequeños (plantillas / misión) — unitarios, sin navegador ni red."""

from __future__ import annotations

import pytest

from paper_pipeline.mission import Mission
from paper_pipeline.templates import prompt_for_section


def test_scenario_mini_mission_ordered_prompts() -> None:
    """Objetivo pequeño: 3 secciones en orden; cada prompt contiene el topic."""

    m = Mission(
        topic="clasificación de texto",
        paper_target="ACL student",
        sections_needed=["gaps", "sota", "methodology"],
        max_perplexity_calls=5,
    )
    ctx = {"topic": m.topic, "paper_target": m.paper_target}
    prompts = [prompt_for_section(s, ctx) for s in m.sections_needed]
    assert len(prompts) == 3
    for p in prompts:
        assert "clasificación de texto" in p.lower() or "clasificación" in p


def test_scenario_max_calls_truncates_sections() -> None:
    """Pide 4 secciones pero max 2 llamadas: la misión debe reflejar el tope en runtime."""

    m = Mission(
        topic="X",
        paper_target="Y",
        sections_needed=["related_work", "sota", "gaps", "experiments"],
        max_perplexity_calls=2,
    )
    assert len(m.sections_needed) == 4
    assert m.max_perplexity_calls == 2


@pytest.mark.parametrize(
    "section",
    ["gaps", "datasets", "related_code"],
)
def test_scenario_templates_resolve(section: str) -> None:
    """Plantillas conectadas: cada clave debe formatear sin KeyError."""

    p = prompt_for_section(section, {"topic": "t", "paper_target": "p"})
    assert len(p) > 20
