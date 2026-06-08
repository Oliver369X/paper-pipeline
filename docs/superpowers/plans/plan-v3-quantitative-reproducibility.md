# Plan v3 — Hacer el preprint genuinamente cuantitativo y reproducible

> **Objetivo:** que un lector externo pueda clonar el repo, correr comandos documentados, obtener números comparables a los del paper (dentro de lo que cada tipo de métrica permite), y entender qué claims son **falsificables** y cuáles son **instantáneas de ejecución**.

> **Cambio respecto a v2:** v2 resolvía el *framing*. v3 resuelve la *evidencia* documentada. v3 asume el framing de v2 ya integrado en el repo.

> **Ajuste al estado del repo (abril 2026):** el fixture CI `examples/safety_usecase` produce **2** candidatos a claims deterministas (no 0): ver `outputs/evidence/claims.json` tras `python scripts/safety_usecase_repro.py`. La condición B contrasta **pipeline completo con ledger** (misión `4f6715a65f4c`) frente a **fixture sin Perplexity** (P2), no dos formas idénticas de artefactos.

---

## Por qué el orden importa

```
Fase 0 → Fase 1 → Fase 2 → Fase 3
verificar    baseline    segunda      paper
reproduct.   contraste   misión       actualizado
```

Si los números del snapshot actual no están auditados, una segunda misión suma ruido. El lector intentará primero reproducir lo **documentado** (harness CI, fixture P2, lectura de JSON de la misión de referencia).

---

## Fase 0 — Verificar reproducibilidad de los números actuales

**Entregable:** [`docs/REPRODUCIBILITY_NOTES.md`](../../REPRODUCIBILITY_NOTES.md) y, opcionalmente, `python scripts/audit_abstract_numbers.py`.

**Script:** [`scripts/audit_abstract_numbers.py`](../../../scripts/audit_abstract_numbers.py) — tabla Markdown desde JSON en disco.

---

## Fase 1 — Condición de contraste mínima (Tabla 1)

**Entregable:** [`docs/preprint/COMPARATIVE_TABLES.md`](../../preprint/COMPARATIVE_TABLES.md) — condición A (misión completa) vs B (fixture P2).

---

## Fase 2 — Segunda misión

**Operativa:** crear `data/missions/<id>/`, ejecutar pipeline, documentar números. Plantilla: [`docs/templates/mission_v3_checklist.md`](../../templates/mission_v3_checklist.md). Runbook: [`data/missions/README_ADDING_MISSION_V3.md`](../../../data/missions/README_ADDING_MISSION_V3.md).

Hasta que exista una segunda misión con `outputs/` completos, la **Tabla 2** en `COMPARATIVE_TABLES.md` lleva marcador de pendiente.

---

## Fase 3 — Preprint

Actualizar [`docs/preprint/PREPRINT_DRAFT.md`](../../preprint/PREPRINT_DRAFT.md), [`PREPRINT_SKELETON.md`](../../PREPRINT_SKELETON.md), [`actualizacion-31-3.md`](../../actualizacion-31-3.md), [`PREPRINT_ARTIFACTS.md`](../../PREPRINT_ARTIFACTS.md).

---

## Cronograma sugerido (referencia)

| Días | Fase |
|------|------|
| 1–3 | Fase 0 |
| 4–5 | Fase 1 |
| 6–12 | Fase 2 (operador) |
| 13–15 | Fase 3 texto |

---

## Enlaces relacionados

- [mio.md](mio.md) — plan canónico B+C  
- [ESTADO_PLAN_PREPRINT_V2.md](../../ESTADO_PLAN_PREPRINT_V2.md) — Plan v2 vs repo  
- [REPRODUCIBILITY_NOTES.md](../../REPRODUCIBILITY_NOTES.md) — auditoría de números
