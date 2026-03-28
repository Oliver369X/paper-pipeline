# Capas de evaluación

## Capa 1 — Revisión asistida (`quality_check`)

- **Implementación:** [quality_phase.py](../../paper_pipeline/pipeline/quality_phase.py): una llamada a Perplexity con el borrador completo y [QUALITY_CHECK_TEMPLATE](../../paper_pipeline/templates.py).
- **Límite:** el mismo *backend* y familia de modelo que las secciones puede **sesgar** la revisión (auto-evaluación). Es útil para lista de gaps y estilo, **no** como garantía de corrección empírica o de reproducibilidad.

## Capa 2 — Extracción determinista de claims

- **Implementación:** [claim_extractor.py](../../paper_pipeline/validation/claim_extractor.py) escribe `outputs/evidence/claims.json` y `claims_evidence_checklist.json`.
- **Propósito:** marcar candidatos a claims cuantitativos o fuertes para revisión humana o trazabilidad.

## Capa 3 — Revisión externa (recomendada para rigor)

Opciones que el repo **no automatiza por defecto**:

- **Modelo distinto** (otro proveedor o API) sobre el mismo borrador.
- **Revisión humana** sobre `claims_evidence_checklist.json` y tablas de baselines (ver [BASELINES_AND_METRICS_TEMPLATE.md](../BASELINES_AND_METRICS_TEMPLATE.md)).

Variables opcionales futuras (documentación; implementación parcial según producto):

- `QUALITY_CHECK_SECONDARY_ENABLED` — si en el futuro se cablea un segundo paso de calidad.
