"""Claves de sección alineadas con `templates.SECTION_PROMPTS` (única fuente de verdad)."""

from __future__ import annotations

from paper_pipeline.templates import SECTION_PROMPTS

_DEFAULT_IF_EMPTY: list[str] = [
    "related_work",
    "sota",
    "gaps",
    "methodology",
    "experiments",
]

# Textos cortos para la UI (español). `output` = archivo típico por sección Perplexity.
SECTION_META_ES: dict[str, dict[str, str]] = {
    "related_work": {
        "title": "Trabajo relacionado",
        "summary": "Bibliografía anotada, BibTeX y hallazgos agrupados (literatura reciente).",
        "output": "outputs/related_work.md",
    },
    "sota": {
        "title": "Estado del arte",
        "summary": "SOTA: benchmarks, métricas, puntuaciones y paradigmas habituales.",
        "output": "outputs/sota.md",
    },
    "gaps": {
        "title": "Brechas",
        "summary": "Problemas abiertos y lagunas metodológicas alineadas al venue.",
        "output": "outputs/gaps.md",
    },
    "datasets": {
        "title": "Datasets",
        "summary": "Datasets públicos: URL, licencia, tamaño, modalidades y advertencias.",
        "output": "outputs/datasets.md",
    },
    "methodology": {
        "title": "Metodología",
        "summary": "Propuesta de método: formulación, baselines, esquema y resultado mínimo viable.",
        "output": "outputs/methodology.md",
    },
    "experiments": {
        "title": "Experimentos",
        "summary": "Plan experimental: baselines, métricas, ablaciones y tabla de resultados (Markdown).",
        "output": "outputs/experiments.md",
    },
    "related_code": {
        "title": "Código relacionado",
        "summary": "Repos y librerías open source con URL, licencia y relevancia (no genera código ejecutable).",
        "output": "outputs/related_code.md",
    },
    "writing_hook": {
        "title": "Gancho de escritura",
        "summary": "Párrafo inicial para enganchar al lector (sin números inventados).",
        "output": "outputs/writing_hook.md",
    },
    "abstract": {
        "title": "Abstract",
        "summary": "Abstract estructurado (Background, Gap, Method, Results, Conclusion).",
        "output": "outputs/abstract.md",
    },
}

OUTPUTS_HELP_ES = (
    "Salidas típicas (relativas a la carpeta outputs/ de la misión): "
    "cada sección de la lista genera un .md con el mismo nombre (p. ej. gaps.md). "
    "Al final del pipeline, draft_paper.md junta el borrador. "
    "Si activás «Código», se crea outputs/code/README.md como guía; el código ejecutable lo añade "
    "el paso Cursor CLI (agent) o vos manualmente en outputs/code/. "
    "Los tests del proyecto van en tests/ (pytest), no dentro de la misión."
)


def section_meta_for_api() -> dict[str, dict[str, str]]:
    """Solo claves que existen en SECTION_PROMPTS."""
    return {k: SECTION_META_ES[k] for k in SECTION_PROMPTS if k in SECTION_META_ES}


def allowed_section_keys() -> list[str]:
    return sorted(SECTION_PROMPTS.keys())


def normalize_sections_needed(sections: list[str]) -> list[str]:
    """Orden estable, sin duplicados; solo claves con plantilla. Si queda vacío, default del modelo Mission."""
    allowed = set(SECTION_PROMPTS.keys())
    seen: set[str] = set()
    out: list[str] = []
    for s in sections:
        if s in allowed and s not in seen:
            out.append(s)
            seen.add(s)
    return out if out else list(_DEFAULT_IF_EMPTY)
