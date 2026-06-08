# Notas de reproducibilidad (Plan v3, Fase 0)

Este documento audita los **números citados en el abstract / borrador del preprint** frente a artefactos en disco y clasifica qué es **determinista** (cualquier clon del repo obtiene lo mismo) frente a **instantánea de ejecución** (depende de entorno, credenciales o modelo).

**Plan maestro:** [superpowers/plans/plan-v3-quantitative-reproducibility.md](superpowers/plans/plan-v3-quantitative-reproducibility.md).

---

## 1. Tabla de auditoría (misión de referencia `4f6715a65f4c`)

| Número en el texto | Valor en snapshot actual | Fuente | Clase |
|--------------------|--------------------------|--------|--------|
| Wall clock ~281 s | **280.554 s** (ledger `started_at` → `ended_at`) | `data/missions/4f6715a65f4c/outputs/run_ledger.json`, run_id `2026-03-29T06-12-37Z__cca251fe` | **Snapshot** - red, Perplexity, Cursor, CPU pueden cambiar el total; el abstract puede decir "~281 s" como redondeo. |
| 21 claim candidates | **21** | `.../outputs/evidence/claims.json` (array) | **Snapshot** - depende del borrador generado en ese run (LLM/Perplexity). Re-ejecutar la misión **no** garantiza el mismo conteo sin el mismo pipeline de generación. |
| Triage tier 2 | **tier 2**, label `insufficient_metrics` | `.../outputs/triage/triage_report.json`, `publication/publish_decision.json` | **Snapshot** - puede variar si cambian métricas, `PAPER_PIPELINE_RELAX_METRICS`, o el bundle de métricas. |
| `planning_only` | **`planning_only`** | `.../outputs/metrics.json` (`replication_tier`, `experiment_runner`) | **Snapshot** - en este snapshot faltaba numpy/HF según `metrics.json`; instalar `[experiments]` / `[llm]` puede cambiar el tier. |
| Fases en ledger | **9** fases con `name` | `run_ledger.json` → `phases` | **Snapshot** - la lista de fases depende de flags de misión (Notion, Cursor, etc.). |
| agent_eval 12/12 @ 1.0 | 12 escenarios, baseline 1.0 | `python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json` | **Determinista** - sin red; `pytest tests/test_agent_eval_baseline.py`. |

**Regenerar la tabla en Markdown (stdout):**

```bash
python scripts/audit_abstract_numbers.py
python scripts/audit_abstract_numbers.py --mission-outputs data/missions/4f6715a65f4c/outputs
```

---

## 2. Comandos exactos por tipo de evidencia

### Determinista (CI, sin claves)

```bash
pip install -e ".[dev]"
pytest tests/test_agent_eval_baseline.py -q
python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json
```

```bash
python scripts/safety_usecase_repro.py
pytest tests/test_safety_usecase_repro.py -q
```

### Fixture P2 (claims deterministas, sin misión completa)

- Salida: `examples/safety_usecase/outputs/evidence/claims.json` (**2** filas en el repo actual).
- No hay `run_ledger.json` de pipeline completo; el trace mínimo está en `build_minimal_safety_usecase_trace()` (ver `paper_pipeline/reporting/case_study_trace.py`).

### Misión completa con Perplexity / Cursor

- Requiere credenciales y configuración documentadas en [GUIA_PRUEBAS_Y_DEBUG.md](GUIA_PRUEBAS_Y_DEBUG.md), [VARIABLES_Y_FLAGS.md](VARIABLES_Y_FLAGS.md).
- **No** se puede prometer el mismo wall clock ni el mismo número de claims que el snapshot `4f6715a65f4c` sin repetir condiciones.

---

## 3. Criterio de redacción para el paper

- Tratar **12/12 agent_eval** y el baseline JSON como números **exactos** bajo la versión actual de escenarios.
- Tratar **wall clock**, **conteo de claims** y **tier** como **instantáneas** ligadas al snapshot (commit / fecha en `run_ledger.json`), no como constantes físicas.
- Si un revisor re-ejecuta la misión, esperar **varianza**; el valor científico honesto es la **trazabilidad** (ledger + métricas + triaje), no la igualdad byte a byte con el abstract.

---

## 4. Comparación condición completa vs CI-only (Fase 1)

Ver tabla detallada en [preprint/COMPARATIVE_TABLES.md](preprint/COMPARATIVE_TABLES.md).

---

## 5. Segunda misión (Fase 2)

Hasta completar una segunda carpeta bajo `data/missions/<id>/` con `outputs/` completos, los números de **Tabla 2** en `COMPARATIVE_TABLES.md` permanecen como **pendiente**. Runbook: [README_ADDING_MISSION_V3.md](../data/missions/README_ADDING_MISSION_V3.md).
