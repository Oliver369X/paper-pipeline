# Esqueleto del preprint (Plan v2 + Plan v3 evidencia) — una página de verdad

Este archivo cumple el rol de **`PREPRINT_SKELETON.md`**: claim en una frase, abstract con **corchetes explícitos** donde faltan datos o son honestos, tabla de secciones, y **afirmación → artefacto** para no sobre-prometer. El **Plan v3** añade tablas comparativas y notas de reproducibilidad ([`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md), [`preprint/COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md)).

---

## Claim central (una oración)

> Presentamos **paper-pipeline**: arquitectura reutilizable para investigación asistida por IA con control explícito de costos, secretos y pasos opcionales; y demostramos su aplicación a un **caso de estudio** en torno a replicación / memorización (arXiv:2510.24256) con **trazas auditables** y límites explícitos sobre qué queda automatizado en CI frente a lo que requiere GPU o cierre humano.

---

## Título sugerido (inglés)

**paper-pipeline: Auditable Infrastructure for AI-Assisted Research — A Case Study Toward Safety-Critical Paper Replication**

*(Alternativa más corta: **paper-pipeline: Ledger, Triage, and Deterministic Agent Evaluation for Reproducible Research Pipelines**)*

---

## Abstract (borrador — rellenar o sustituir corchetes)

> Reproducible research in AI safety and mechanistic interpretability still lacks **shared infrastructure** for the repeatable parts of the cycle—drafting, instruction loops, metric hooks, and publication gates—while keeping **auditability** first-class. We present **paper-pipeline**, an open-source system that records execution in a **ledger**, triages mission metrics, runs a **deterministic agent_eval harness** (no LLM API in CI), and exports **supplementary bundles** for preprints. We report a **reference mission** on arXiv:2510.24256 with wall-clock runtime **[≈281 s]**, **[21]** heuristic claim candidates extracted from the assembled draft, triage tier **[2]** (insufficient empirical metrics for a breakthrough claim), and experiment capability **[planning_only]** under optional HF dependencies. Separately, a **CI-only fixture** yields **[2]** deterministic claim rows (not 21) without Perplexity. The harness passes **[12/12]** bundled governance scenarios at rate **[1.0]** (exact, reproducible). A **second** full mission row in comparative tables is **[pendiente]**. We do **not** claim end-to-end numerical replication of the target paper’s experiments in this artifact snapshot.

**Corchetes con datos reales (repo actual):**  
`[≈281 s]` — snapshot `run_ledger.json` misión `4f6715a65f4c` (inicio/fin; **no** garantizado al re-ejecutar).  
`[21]` — filas en `evidence/claims.json` de esa misión.  
`[2]` — claims en fixture `examples/safety_usecase` tras `safety_usecase_repro.py`.  
Triage **`[2]`** / `insufficient_metrics` — `triage_report.json` (misión completa).  
`[planning_only]` — `metrics.json` capability path.  
`[12/12]` y `[1.0]` — `agent_eval` + baseline.

---

## Tabla de secciones ↔ artefacto que las sostiene

| Sección (borrador) | Contenido clave | Artefacto / evidencia |
|--------------------|-----------------|------------------------|
| 1. Introduction | Problema reproducibilidad + gap infra | `PREPRINT_CLAIM.md`, PaperBench/MIB refs |
| 2. Related Work | PaperBench, MIB, Merullo, tooling | `PREPRINT_CLAIM.md` tabla |
| 3. System Design | Ledger, triaje, harness, figuras | `01-arquitectura.md`, `status-matrix.md`, `docs/assets/*.mmd` |
| 4. Auditable harness | Escenarios, baseline, regresión | `examples/baselines/`, `tests/test_agent_eval_baseline.py` |
| 5. Case study | Misión real + límites empíricos | `data/missions/4f6715a65f4c/outputs/`, `case_study_trace.json` (appendix) |
| 5.2–5.3 | Comparación A vs B; segunda misión (pendiente) | [`COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md), [`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md) |
| 5b. CI fixture | Claims sin API (2 deterministas) | `examples/safety_usecase/` |
| 6. Limitations | Modo narrativo, N=1 vs N=2, varianza | `MODE_NARRATIVE_VS_EMPIRICAL.md`, `metrics.json`, Plan v3 |
| 7. Conclusion | Puente infra + trabajo futuro | — |
| App. A | Bundle reproducibilidad | `paper-export-appendix` → `case_study_trace.json` + resto |
| App. B | Baseline harness | `agent_eval_baseline.json` |

---

## Afirmaciones que el paper **sí** hace (con evidencia)

1. El diseño expone **ledger + triaje + publish signals** — `run_ledger.json`, `publish_decision.json`.
2. El **agent_eval** es **determinista** y tiene **baseline versionado** — tests + JSON.
3. El **caso de estudio** documenta una corrida real con **tier 2** y réplica **degradada** a nivel empírico — honestidad explícita.
4. Hay **exportación de appendix** sin secretos — `appendix_export.py`.

## Afirmaciones que el paper **no** hace (cláusula)

- No es benchmark entre pipelines.
- No entrena modelo nuevo.
- No mide ganancia de tiempo con usuarios (salvo orden de magnitud en informe P2).
- No garantiza réplica numérica del paper Merullo en GPU solo con este repo.

---

## Criterio de hecho

Cualquier coautor puede escribir el `.tex` / Word leyendo este esqueleto + [`PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md) + [`PREPRINT_ARTIFACTS.md`](PREPRINT_ARTIFACTS.md).
