# Checklist - segunda misión (Plan v3 Fase 2)

Usar antes y después de `paper-pipeline` / `paper-loop` sobre un paper ancla nuevo.

## Antes del run

- [ ] `mission.md` con `paper_target` / tema alineado al paper elegido.
- [ ] Credenciales y flags documentados (Perplexity, Notion, Cursor si aplica).
- [ ] Entorno: nota de versión Python y extras pip (`[llm]`, `[experiments]`).

## Después del run (artefactos mínimos para Tabla 2)

- [ ] `outputs/run_ledger.json` con `started_at` / `ended_at`.
- [ ] `outputs/evidence/claims.json`.
- [ ] `outputs/metrics.json` y `outputs/triage/triage_report.json`.
- [ ] `outputs/publication/publish_decision.json` (si aplica).

## Documentación

- [ ] Añadir fila a [preprint/COMPARATIVE_TABLES.md](../preprint/COMPARATIVE_TABLES.md) Tabla 2.
- [ ] Opcional: `paper-export-appendix --case-study-outputs .../outputs -o /tmp/appendix_m2`.
