# gpt-researcher

## Patrón principal

Planner genera sub-preguntas; ejecutores paralelos recopilan fuentes; curator filtra; writer produce informe con referencias.

## 3 ideas adoptables

1. `research_plan.json` con queries por sección (implementado).
2. `SourceCurator` — scoring LLM de URLs (implementado en `source_curation.py`).
3. Cost tracking por fase en manifest/ledger.

## Archivos fuente

- `research-repos/gpt-researcher/gpt_researcher/skills/researcher.py`
- `research-repos/gpt-researcher/gpt_researcher/skills/curator.py`

## Mapeo paper-pipeline

- `pipeline/research_plan_phase.py`
- `pipeline/source_curation.py`

## Riesgo / limitación

Requiere APIs de búsqueda (Tavily); Mistral no reemplaza crawlers.

## Prioridad

P0
