# Tablas comparativas (Plan v3)

Números medidos sobre el repo en **abril 2026** salvo donde se indique. Para regenerar conteos del harness usar los comandos en [REPRODUCIBILITY_NOTES.md](../REPRODUCIBILITY_NOTES.md).

---

## Tabla 1 - Condición completa (A) vs fixture CI-only (B)

**A** = misión de referencia Merullo et al., arXiv:2510.24256, `data/missions/4f6715a65f4c/outputs/` (snapshot con `run_ledger.json`).

**B** = caso P2, `examples/safety_usecase/` - sin Perplexity; claims vía `python scripts/safety_usecase_repro.py` (determinista).

| Observable | A: Full pipeline (`4f6715a65f4c`) | B: CI fixture (`safety_usecase`) |
|------------|-----------------------------------|-----------------------------------|
| `run_ledger.json` (fases de misión) | Sí - **9** fases nombradas | No - no es una misión ejecutada con el runner completo |
| Triage / tier | Sí - **tier 2** (`insufficient_metrics`) | No - trace mínimo sin triaje de misión; ver `build_minimal_safety_usecase_trace` |
| `publish_decision` / señales | Sí | No en el fixture (solo manifest + claims) |
| Claim candidates (`claims.json`) | **21** | **2** (deterministas tras `safety_usecase_repro.py`) |
| `metrics.json` / `replication_tier` | Sí - `planning_only` (numpy/HF ausentes en snapshot) | No |
| APIs externas | Perplexity + integraciones según ledger | Ninguna |
| Wall clock (orden de magnitud) | **~281 s** (280.554 s en ledger) | **~1 s** (medición local de `safety_usecase_repro.py`; depende de CPU) |
| Appendix exportable (`paper-export-appendix`) | Sí - trace completo + `benchmark_bundle` | Parcial - fallback P2 si no hay misión por defecto |

**Lectura:** la tabla no es un "benchmark ML"; describe **qué capas** aparecen solo cuando se corre el pipeline completo (ledger, triaje, métricas) frente al fixture mínimo en CI.

---

## Tabla 2 - Dos misiones de referencia (Merullo vs segunda misión)

**Misión 1** = `4f6715a65f4c` (arXiv:2510.24256) - valores del snapshot actual.

**Misión 2** = *pendiente* - completar tras ejecutar el Plan v3 Fase 2 (ver [README_ADDING_MISSION_V3.md](../../data/missions/README_ADDING_MISSION_V3.md)). Renombrar esta tabla cuando exista `data/missions/<id>/outputs/`.

| Observable | Misión 1 (Merullo) | Misión 2 (TBD) |
|------------|---------------------|----------------|
| `mission_id` | `4f6715a65f4c` | *Runbook: añadir tras crear misión* |
| Wall clock | ~281 s | *Pendiente* |
| Claim candidates | 21 | *Pendiente* |
| Triage tier | 2 | *Pendiente* |
| `replication_tier` / capability | `planning_only` | *Pendiente* |
| APIs externas | Perplexity + (según ledger) Cursor, Notion | *Pendiente* |
| Appendix / `case_study_trace` | Sí | *Pendiente* |

**Placeholder de carpeta:** [plan_v3_mission2_placeholder/README.md](../../data/missions/plan_v3_mission2_placeholder/README.md) (instrucciones; no sustituye una misión real).
