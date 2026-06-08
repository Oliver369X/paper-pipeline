# Síntesis del proyecto (actualizada) — paper-pipeline, plan `mio`, Plan v2/v3 y preprint

Documento **único** de síntesis para vos, para onboarding rápido y **para compartir con un mentor** antes de pedir feedback serio. Incluye: mensaje del trabajo, qué está implementado según [`mio.md`](superpowers/plans/mio.md), el **Plan v2** (framing) y el **Plan v3** (evidencia cuantitativa y tablas comparativas), enlaces concretos y una sección **“qué preguntarle al mentor”** para obtener comentarios accionables.

**Última actualización de este archivo:** abril 2026 (sigue siendo válido el contexto del 31-03 como hito inicial).

---

## 1. A dónde apunta el trabajo (mensaje claro)

**Intención:** presentar **paper-pipeline** como **infraestructura** de investigación asistida por IA: trazas en disco (`run_ledger.json`), triaje y señales de publicación, harness de gobernanza **determinista** en CI (`agent_eval`), exportación de anexos sin secretos — no solo como “otro asistente de escritura”.

**Paper ancla narrativo:** arXiv:2510.24256 (Merullo et al.), usado en el caso P2 y en la **misión de referencia** `data/missions/4f6715a65f4c/` (honesta sobre **tier 2**, **planning_only** cuando faltan dependencias opcionales).

**Lo que sí podés decir con seguridad:**

- Artefactos **revisables** (ledger, claims heurísticos, `agent_eval` con baseline versionado) y **tests en CI sin Perplexity**.
- Caso **mínimo reproducible en CI:** `examples/safety_usecase/` con límites explícitos.
- **Misión real** con ledger + `case_study_trace` / `benchmark_bundle` para el manuscrito sobre el sistema.
- Borrador de preprint en inglés + esqueleto + tabla de artefactos.

**Lo que no conviene prometer sin matiz:** Claim A (productividad medida), réplica numérica completa del paper Merullo solo con el repo, o “AI safety” en sentido de alineación extremo sin definir — ver [`PREPRINT_CLAIM.md`](PREPRINT_CLAIM.md).

---

## 2. Plan v2 preprint vs repo (checklist resumida)

El detalle línea por línea está en [`ESTADO_PLAN_PREPRINT_V2.md`](ESTADO_PLAN_PREPRINT_V2.md). Resumen:

| Ítem Plan v2 | Estado |
|--------------|--------|
| `PREPRINT_SKELETON.md` (claim, abstract con corchetes, tabla sección→artefacto) | Hecho |
| `PREPRINT_ARTIFACTS.md` | Hecho |
| Baseline `agent_eval` + tests | Hecho |
| `case_study_trace.json` en export de appendix | Hecho (`paper-export-appendix`, `--case-study-outputs`) |
| Figura flujo case study (`case_study_replication_flow.mmd` + PNG) | Hecho |
| Borrador preprint + números reales (duración, claims, tier, harness) | Hecho en [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md) |
| Caso “replicación real” completa en GPU | **No** empaquetado; misión de referencia con **planning_only** documentado |
| Related work pulido para envío | **Parcial** (sigue siendo trabajo humano) |

---

## 2b. Plan v3 — evidencia cuantitativa y reproducible

Plan canónico: [`superpowers/plans/plan-v3-quantitative-reproducibility.md`](superpowers/plans/plan-v3-quantitative-reproducibility.md).

| Fase | Entregable en repo | Estado |
|------|---------------------|--------|
| 0 | [`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md) + `python scripts/audit_abstract_numbers.py` + `paper_pipeline/reporting/abstract_audit.py` | Hecho |
| 1 | [`preprint/COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md) Tabla 1 (misión completa vs fixture P2) | Hecho |
| 2 | Segunda misión bajo `data/missions/` con `outputs/` completos + Tabla 2 | **Pendiente** (runbook: [`README_ADDING_MISSION_V3.md`](../data/missions/README_ADDING_MISSION_V3.md), placeholder [`plan_v3_mission2_placeholder`](../data/missions/plan_v3_mission2_placeholder/README.md)) |
| 3 | Texto: [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md), [`PREPRINT_SKELETON.md`](PREPRINT_SKELETON.md) | Hecho (abstract/limitaciones actualizados; Tabla 2 explícitamente pendiente) |

---

## 3. Qué dice `mio.md` y qué quedó implementado (P-1 … P4 + extensiones)

El plan canónico es [`superpowers/plans/mio.md`](superpowers/plans/mio.md). Mapeo:

| Entrega en `mio` | Estado | Dónde está |
|------------------|--------|------------|
| **P-1** — claridad de claims (`PREPRINT_CLAIM.md`) | Hecho | [`PREPRINT_CLAIM.md`](PREPRINT_CLAIM.md) |
| **P0** — tabla artefactos (`PREPRINT_ARTIFACTS.md`) | Hecho + ampliado con `benchmark_bundle`, appendix | [`PREPRINT_ARTIFACTS.md`](PREPRINT_ARTIFACTS.md) |
| **P1** — baseline `AgentEvalBaseline`, JSON, `--check-baseline`, tests | Hecho | `paper_pipeline/agent_eval/baseline_spec.py`, `examples/baselines/`, `tests/test_agent_eval_baseline.py` |
| **P2** — safety use case mínimo | Hecho | `examples/safety_usecase/`, `tests/test_safety_usecase_repro.py` |
| **P3** — `paper-export-appendix` | Hecho y **extendido** | `VERSION`, `git_commit`, `agent_eval_report.json`, `pytest_collect.txt`, **`case_study_trace.json`**, **`benchmark_bundle.json`**, **`benchmark_table.md`** (un solo `run_all` del harness) |
| **P4** — figuras arquitectura | Hecho + **extra** | `docs/assets/*.mmd`, figuras preprint enriquecidas vía `scripts/generate_preprint_figures.py` (per-scenario, ejes, radar, duración por fase, claims) |

**Extensiones fuera del texto original de `mio` pero alineadas al argumento del paper:**

- `paper_pipeline/reporting/case_study_trace.py` — agregación redactada desde `outputs/` de misión.
- `paper_pipeline/reporting/benchmark_bundle.py` — JSON + `benchmark_bundle_to_markdown_table()`; CLI `python -m paper_pipeline.reporting.benchmark_bundle`.
- `paper_pipeline/reporting/preprint_figures.py` — figuras matplotlib adicionales.
- `docs/PREPRINT_SKELETON.md`, `docs/preprint/PREPRINT_DRAFT.md` (borrador en inglés).
- CI: `.github/workflows/pytest-focused.yml` incluye tests de appendix, benchmark y figuras preprint.

**Qué sigue abierto en `mio` (checklist global):** pulir **redacción final** del paper (LaTeX/venue), related work con citas formales, y cualquier **Claim A** (usuarios/tiempos) como trabajo futuro.

---

## 4. Recorrido “3 minutos” para mostrar el proyecto

| Orden | Archivo | Qué contar |
|-------|---------|------------|
| 1 | [`PREPRINT_CLAIM.md`](PREPRINT_CLAIM.md) | Claims B+C y qué **no** se afirma. |
| 2 | [`PREPRINT_ARTIFACTS.md`](PREPRINT_ARTIFACTS.md) | Evidencias y comandos para revisores. |
| 3 | [`examples/safety_usecase/report.md`](../examples/safety_usecase/report.md) | Caso P2 sin API en CI. |
| 4 | Misión `4f6715a65f4c` + `outputs/run_ledger.json` | Run real con fases (Perplexity, Cursor, etc.). |
| 5 | [`preprint/README.md`](preprint/README.md) + `docs/preprint/figures/` | Figuras + cómo regenerar. |
| 6 | [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md) | Borrador en inglés + sección *Mentor briefing*. |

Técnica extra: `examples/baselines/agent_eval_baseline.json` + `paper-agent-eval-check`.

---

## 5. Conceptos que no conviene mezclar

| Concepto | Qué es aquí |
|----------|-------------|
| **Misión** | Unidad de trabajo (`mission.md` + `outputs/`). |
| **Paper ancla** | arXiv:2510.24256 — contexto; la réplica empírica completa **no** está garantizada. |
| **Baseline `agent_eval`** | Regresión de oráculos del harness en CI — **no** compara con Merullo en GPU. |
| **Métricas ML en `metrics.json`** | Otro nivel: depende del experiment runner y del entorno (puede ser `planning_only`). |

---

## 6. Para tu mentor: cómo pedir feedback que sirva

**Objetivo:** que te digan algo que puedas **accionar** (venue, claims, experimentos mínimos), no solo “está bien”.

### 6.1 Qué archivos adjuntar o enlazar

1. [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md) — borrador en inglés (incluye *Mentor briefing* y preguntas abiertas).
2. [`PREPRINT_CLAIM.md`](PREPRINT_CLAIM.md) — límites del claim.
3. Opcional: [`PREPRINT_ARTIFACTS.md`](PREPRINT_ARTIFACTS.md) — si le interesa la reproducibilidad técnica.

### 6.2 Preguntas concretas (elegí las que apliquen)

- **Venue:** ¿Este trabajo lo ves más como *systems / MLSys / arXiv tech report*, *HCI/tools*, o *workshop* de reproducibilidad, que como *main track* ICML/NeurIPS sin métricas ML nuevas?
- **Claims:** ¿El híbrido B+C (arquitectura + caso safety honesto) te parece defendible o conviene **estrechar** el claim?
- **Evaluación:** ¿Qué experimento **mínimo** haría falta para que el trabajo sea creíble para vos: usuario N=5, una métrica reproducida en GPU, o ablación con/sin pipeline?
- **Historia:** ¿La tensión “tier 2 + planning_only” se lee como **fortaleza** (honestidad) o como **debilidad** que conviene acortar en el texto?
- **Related work:** ¿Falta algún hilo obligatorio (PaperBench, MIB, herramientas tipo DSPy/LangChain) en un párrafo?

### 6.3 Qué dejar explícito al mentor (para no malentendidos)

- `agent_eval` **no** mide calidad del LLM; mide **gobernanza** offline en CI.
- Los **21 claims** son **candidatos heurísticos**, no verificaciones científicas automáticas.
- El **benchmark_bundle** es **auditoría + tiempos de fase**, no accuracy en una tarea downstream.

---

## 7. Pitch corto (elevator)

> *“Construimos infra open source para que el **proceso** de investigación asistida por LLM quede auditado: ledger, triaje, extracción de claims y un harness de gobernanza con baseline en CI. Mostramos un caso mínimo en CI y una misión de referencia anclada a arXiv:2510.24256 con **límites explícitos** (tier 2, planning_only). Hay borrador de preprint en inglés, figuras y bundles de anexo; busco criterio de venue y qué experimento mínimo sumaría credibilidad.”*

---

## 8. Enlaces rápidos

| Necesitás… | Archivo |
|------------|---------|
| Plan maestro | [`mio.md`](superpowers/plans/mio.md) |
| Plan v2 vs repo | [`ESTADO_PLAN_PREPRINT_V2.md`](ESTADO_PLAN_PREPRINT_V2.md) |
| Qué defender | [`PREPRINT_CLAIM.md`](PREPRINT_CLAIM.md) |
| Artefactos / comandos | [`PREPRINT_ARTIFACTS.md`](PREPRINT_ARTIFACTS.md) |
| Esqueleto (corchetes, tablas) | [`PREPRINT_SKELETON.md`](PREPRINT_SKELETON.md) |
| Borrador preprint (inglés) | [`preprint/PREPRINT_DRAFT.md`](preprint/PREPRINT_DRAFT.md) |
| Figuras y regeneración | [`preprint/README.md`](preprint/README.md) |
| Caso P2 | [`examples/safety_usecase/report.md`](../examples/safety_usecase/report.md) |
| Plan v3 (evidencia) | [`superpowers/plans/plan-v3-quantitative-reproducibility.md`](superpowers/plans/plan-v3-quantitative-reproducibility.md) |
| Reproducibilidad / audit números | [`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md) |
| Tablas comparativas (A vs B, misión 2) | [`preprint/COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md) |

---

*Este archivo resume estado de repo y planes; no sustituye el historial de git.*
