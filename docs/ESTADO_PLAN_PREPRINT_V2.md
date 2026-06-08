# Estado del “Plan v2 preprint” frente al repo (mapa de dudas)

Este documento compara el plan que describís (esqueleto + P0–P4 + checklist) con lo que **existe** en **paper-pipeline** a marzo 2026. No sustituye [actualizacion-31-3.md](actualizacion-31-3.md) ni [superpowers/plans/mio.md](superpowers/plans/mio.md).

**Resumen en una frase:** el repo cumple el **brazo B** (arquitectura, harness, baseline, figuras, appendix técnico) y un **caso P2 honesto**; además hay **`PREPRINT_SKELETON.md`**, **`case_study_trace.json`** en el export del appendix, **borrador en inglés** [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md), y el diagrama **`case_study_replication_flow.mmd`**. El **Plan v3** añade [`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md) y [`preprint/COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md) (Tabla 1 A vs B; Tabla 2 pendiente de segunda misión). Lo que sigue siendo trabajo **humano/editorial**: venue, LaTeX, related work pulido, segunda misión con outputs, y cualquier nueva medición de productividad (Claim A).

---

## Checklist del Plan v2 — línea por línea

| Ítem Plan v2 | ¿Hecho en el repo? | Notas |
|--------------|-------------------|--------|
| `PREPRINT_SKELETON.md` (claim, abstract con corchetes, tabla secciones, afirmación→artefacto) | **Sí** | [PREPRINT_SKELETON.md](PREPRINT_SKELETON.md) |
| `PREPRINT_ARTIFACTS.md` como tabla afirmación→evidencia | **Sí** | [PREPRINT_ARTIFACTS.md](PREPRINT_ARTIFACTS.md); baseline citado como `agent_eval_baseline.json` |
| P1: baseline `agent_eval` + tests | **Sí** | `examples/baselines/agent_eval_baseline.json`, `tests/test_agent_eval_baseline.py` |
| P1 extra: comentarios en tests que citan sección del paper | **Parcial** | Docstring / comentarios enlazan al preprint §4 donde aplica; no cada `assert` |
| P2: `paper-export-appendix` | **Sí** | Incluye **`case_study_trace.json`** — ver `appendix_export.py` |
| P2 extra: **`case_study_trace.json`** | **Sí** | Generado por export; default misión `4f6715a65f4c` si hay `run_ledger.json`; CLI `--case-study-outputs` |
| P3: figura arquitectura + flujo replicación case study | **Sí** | `docs/assets/case_study_replication_flow.mmd`; PNG: `preprint/README.md` (`fig_case_study_replication_flow.png`) |
| P4: paper de safety ejecutado end-to-end con traza | **Parcial** | Misión de referencia con ledger + métricas honestas en docs/borrador; **no** réplica numérica GPU completa del paper Merullo |
| Abstract: números reales (duración, claims, tier, harness) | **Sí** en esqueleto y borrador | Ver corchetes en [PREPRINT_SKELETON.md](PREPRINT_SKELETON.md) y abstract en [PREPRINT_DRAFT.md](preprint/PREPRINT_DRAFT.md) |
| Related work ≤1 párrafo por paper | **Parcial** | Esbozado en PREPRINT_CLAIM / DRAFT; pulir para envío |
| Ningún token en artefactos exportados | **Sí** | Política documentada |

---

## Cómo leer el “claim” del Plan v2 vs lo implementado

| Plan v2 dice… | En el repo hoy… |
|---------------|-----------------|
| “UN caso de replicación **real**” para el brazo C | Caso **documentado** = misión `4f6715a65f4c` + `case_study_trace.json` + texto honesto sobre **planning_only** / tier 2. Réplica numérica completa **no** empaquetada como único entregable. |
| “Traza en `case_study_trace.json`” | **Implementado** — JSON agregado sin secretos desde `outputs/` de misión. |
| “P4 antes de P0” en el orden semanal | El desarrollo siguió otro orden; el Plan v2 es guía editorial. |

---

## Qué podría mejorarse después (opcional)

1. Regenerar PNG de todos los Mermaid tras cambios en fuentes (`npx @mermaid-js/mermaid-cli`).
2. Ampliar related work y referencias formales en el borrador para un venue concreto.
3. Comentarios test→§ del paper más granulares si un revisor lo pide.

---

## Conclusión clara

- **Implementado:** infraestructura auditable, harness + baseline, appendix con `case_study_trace`, figuras y diagrama de flujo case study, documentación de claims, esqueleto y borrador de preprint con números coherentes con artefactos.
- **Sigue siendo decisión humana:** envío a arXiv u otro venue, pulido narrativo, y claims de productividad no medidos en repo.
