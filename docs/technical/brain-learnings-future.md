# Patrón tipo OpenClaw `.learnings/` en paper-pipeline (diseño futuro, no v1)

Este documento **no describe comportamiento implementado**. Propone cómo podría adoptarse el **patrón** de lecciones estructuradas (como en skills *self-improvement* del ecosistema OpenClaw: entradas en markdown/JSON con prioridad, estado, área) **sin** que el LLM integre cambios silenciosos en el repositorio.

## Objetivo

- Capturar **fallos repetidos**, **malentendidos sobre capacidades** o **pedidos imposibles** con contexto de misión.
- Mantener **revisión humana** antes de que cualquier texto entre al catálogo L1 (`brain_capabilities.md`) o al código.

## Formato propuesto (bosquejo)

- Ubicación candidata: `outputs/brain_learnings.jsonl` **por misión** (append-only), o entradas en `docs/` solo tras PR.
- Campos sugeridos por línea JSON: `ts`, `mission_id`, `area` (p. ej. `capability_gap` | `user_expectation`), `summary`, `suggested_doc_patch` (texto, no aplicado automáticamente), `status` (`proposed` | `rejected` | `merged_to_repo`).

## Por qué no es v1

- Aumenta superficie de datos y gobernanza (quién aprueba, privacidad entre misiones).
- El plan actual prioriza **catálogo L1 versionado** y **análisis OpenClaw** documentado, no un segundo sistema de memoria episódica paralelo a `research_memory.jsonl`.

## Relación con ResearchMemory

- `research_memory.jsonl` ya registra eventos de pipeline/calidad con `kind` acotado.
- Un futuro `brain_learnings` sería **específico de UX del cerebro** y de documentación; no sustituye triaje ni métricas.
