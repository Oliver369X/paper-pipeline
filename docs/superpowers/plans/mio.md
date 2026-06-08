# Plan — Preprint: paper-pipeline como infraestructura reproducible para AI safety research

> **Claim central (híbrido B+C):**
> *Presentamos una arquitectura open-source para pipelines de investigación asistida por IA — con control explícito de costos, secretos y pasos opcionales — y la validamos en AI safety como caso de uso primario, donde la reproducibilidad y la auditabilidad son requisitos, no opcionales.*

Este documento es el **plan canónico** del preprint (`2026-03-31-preprint-artefactos-mision.md` solo redirige aquí).
La misión del producto no cambia; este plan añade la capa de argumento científico que el plan corto inicial no tenía.

---

## Por qué este claim y no otro

El plan anterior construía artefactos sin tener claro qué afirmaba el paper.
Tres opciones estaban disponibles:

| Claim | Lo que requiere que ya no tenemos |
|-------|-----------------------------------|
| A — Eficiencia medida | Baseline humano, usuarios externos, métricas de tiempo antes/después |
| B — Arquitectura reutilizable | Solo documentación y harness — **disponible hoy** |
| C — Infraestructura safety | Conexión explícita a casos de uso safety — **disponible hoy si la construimos** |

**El híbrido B+C es honesto y fuerte:** el sistema ya existe como arquitectura (B); el trabajo nuevo es mostrar que el diseño es especialmente valioso para el problema específico de reproducibilidad en safety research (C). No infla, no promete mediciones que no tenemos.

---

## Qué afirma el paper — en tres niveles

### Afirmación de sistemas (Claim B — ya demostrable)
> La combinación de ledger determinista + triaje + agent_eval + control explícito de costos y secretos es un patrón de diseño reutilizable para pipelines de investigación asistida por IA que otros equipos pueden adaptar con garantías reproducibles.

**Evidencia disponible:** arquitectura documentada, harness determinista, baseline de agent_eval, tests.

### Afirmación de aplicación (Claim C — trabajo nuevo acotado)
> Este patrón es especialmente relevante para AI safety research, donde: (1) los papers frecuentemente no se replican, (2) las evaluaciones no son comparables entre equipos, y (3) la auditabilidad del proceso de investigación importa tanto como el resultado.

**Evidencia requerida:** una demostración concreta de que el pipeline puede procesar un paper de safety, extraer claims, ejecutar código asociado, y producir un reporte de reproducibilidad. No necesita ser exhaustiva — un ejemplo bien documentado es suficiente para el preprint.

### Afirmación de posicionamiento (contexto para la comunidad)
> La infraestructura existe hoy para hacer investigación de safety más rápida y acumulativa. El cuello de botella no es técnico — es que nadie ha construido el puente entre los componentes dispersos. Este sistema es ese puente.

**Evidencia requerida:** sección de related work que muestre el gap. PaperBench (arXiv:2504.01848) y MIB (arXiv:2504.13151) son los dos papers ancla.

---

## Esqueleto del paper (para orientar los artefactos)

```
1. Introduction
   — El problema de reproducibilidad en AI safety research
   — Por qué la solución es infraestructura, no más papers
   — Contribución: arquitectura + demostración en safety

2. Related Work
   — PaperBench: el gap de replicación automatizada
   — MIB: el gap de evaluación comparable
   — Herramientas existentes (LangChain, DSPy, etc.) y por qué no resuelven esto

3. System Architecture
   — Diagrama de componentes (ledger, triaje, agent_eval, report-figures)
   — Principios de diseño: control explícito, determinismo, auditabilidad
   — Tabla: qué contrato ofrece cada componente

4. Evaluation (agent_eval harness)
   — Descripción del harness determinista
   — Escenarios: goal selection, safety checks, cost control
   — Baseline versionado y criterio de regresión

5. Safety Research Use Case
   — Pipeline aplicado a un paper ancla de safety (memorización o jailbreak)
   — Reporte de reproducibilidad generado
   — Qué funcionó, qué no, qué requirió ajuste manual

6. Limitations
   — Qué el sistema no automatiza todavía
   — Dónde sigue siendo necesaria la revisión humana
   — Condiciones bajo las que el harness no es suficiente

7. Conclusion & Future Work
   — El puente que faltaba, construido
   — Próximos pasos: escalar a más papers, evaluación multieje
```

---

## Deliverables del plan (orden de prioridad)

### P-1 — Claim clarity doc (solo escritura, sin código) ← NUEVO

**Archivo nuevo:** `docs/PREPRINT_CLAIM.md`

**Contenido:**
- Las tres afirmaciones del paper (sistemas, aplicación, posicionamiento) en lenguaje de paper
- Un párrafo de abstract draft
- Lista de las dos o tres cosas que el paper NO afirma (tan importante como lo que sí afirma)
- Dos preguntas que un reviewer hostil haría, con respuestas honestas

**Criterio de hecho:** cualquier colaborador puede leer este doc y saber exactamente qué estamos defendiendo y qué no.

**Por qué es P-1 y no P0:** sin esto, todos los demás artefactos pueden estar orientados hacia el claim equivocado. Es el único deliverable que desbloquea todos los demás.

---

### P0 — Documento ancla (doc, sin código)

**Archivo nuevo:** `docs/PREPRINT_ARTIFACTS.md`

**Contenido (actualizado respecto al plan anterior):**

Una tabla con cuatro columnas:

| Afirmación del paper | Artefacto | Ruta / comando | Limitación honesta |
|---------------------|-----------|-----------------|-------------------|
| Arquitectura determinista | agent_eval harness | `python -m paper_pipeline.agent_eval` | Solo cubre escenarios sintéticos |
| Reproducibilidad del sistema | baseline versionado | `examples/baselines/agent_eval_baseline.json` | Umbrales definidos por nosotros |
| Aplicabilidad a safety | caso de uso ancla | `examples/safety_usecase/` | Un paper, no una muestra representativa |
| Auditabilidad del proceso | paquete de exportación | `paper-export-appendix` | No incluye tokens ni secretos |

Más: párrafo de límites explícitos (reutilizar tono de `MODE_NARRATIVE_VS_EMPIRICAL.md`).

**Criterio de hecho:** la sección *Methods / Artifacts* del paper puede escribirse leyendo solo este doc.

---

### P1 — Baseline versionado del agent_eval (código mínimo + tests)

Sin cambios respecto al plan anterior — sigue siendo la pieza más valiosa porque da algo falsificable.

**Tareas (implementado):**
1. Modelo Pydantic `AgentEvalBaseline` en `paper_pipeline/agent_eval/baseline_spec.py` + `examples/baselines/agent_eval_baseline.json`.
2. `paper_pipeline/agent_eval/baseline_compare.py`, `--check-baseline` en `python -m paper_pipeline.agent_eval`, wrapper `paper-agent-eval-check`, script `scripts/write_agent_eval_baseline.py`.
3. `tests/test_agent_eval_baseline.py` — sin red, CI-safe.

**Criterio de hecho:** CI falla si el harness empeora sin actualizar el baseline explícitamente.

---

### P2 — Safety use case mínimo ← NUEVO (reemplaza paper-export-appendix como prioridad)

Este es el entregable que diferencia este preprint de un paper de sistemas genérico. Sin él, el Claim C no tiene evidencia.

**Meta:** demostrar que el pipeline puede procesar un paper de safety y producir un reporte de reproducibilidad honesto.

**Implementado (rigor revisable):** ancla arXiv:2510.24256 + `examples/safety_usecase/` con `report.md`, `fixture_draft.md`, `outputs/evidence/*.json`, `scripts/safety_usecase_repro.py`, `tests/test_safety_usecase_repro.py`. La parte **CI-safe** es extracción determinista de claims (misma ruta que `run_pipeline`); no se afirma réplica GPU ni run Perplexity en CI.

**Scope mínimo:**
- Elegir un paper ancla con código público (sugerido: un paper de memorización con repo GitHub verificado).
- Correr el pipeline sobre ese paper: extracción de claims, ejecución de código, comparación de resultados.
- Producir `examples/safety_usecase/report.md`: qué se replicó exactamente, qué requirió ajuste, qué falló.
- Documentar el tiempo humano invertido en cada paso (esto es data para Claim A en versiones futuras).

**Lo que NO incluye:** generalización a múltiples papers, evaluación comparativa, benchmarking masivo.

**Criterio de hecho:** el reporte existe, es honesto sobre sus límites, y cualquiera puede reproducirlo con el comando documentado.

---

### P3 — paper-export-appendix (desbloqueado; ampliado respecto al texto original)

**Implementado:** CLI `paper-export-appendix -o DIR` escribe, sin secretos: `VERSION`, `git_commit.txt`, `agent_eval_report.json`, `pytest_collect.txt`, **`case_study_trace.json`** (traza agregada desde `outputs/` de misión o fallback P2), **`benchmark_bundle.json`** (harness + trace + tiempos de fase del ledger), **`benchmark_table.md`** (tabla Markdown para anexo). Un solo `run_all` del harness; opción `--case-study-outputs`. Código: [`appendix_export.py`](../../../paper_pipeline/reporting/appendix_export.py), [`benchmark_bundle.py`](../../../paper_pipeline/reporting/benchmark_bundle.py), tests `tests/test_appendix_export.py`, `tests/test_benchmark_bundle.py`.

---

### P4 — Figuras de arquitectura y material preprint (ampliado)

**Implementado:** fuentes Mermaid [`docs/assets/architecture_overview.mmd`](../../assets/architecture_overview.mmd), [`architecture_governance.mmd`](../../assets/architecture_governance.mmd), [`case_study_replication_flow.mmd`](../../assets/case_study_replication_flow.mmd), [`docs/assets/README.md`](../../assets/README.md), scripts `export_architecture_figure.*`, test `tests/test_docs_assets.py`.

**Adicional:** `scripts/generate_preprint_figures.py` + [`preprint_figures.py`](../../../paper_pipeline/reporting/preprint_figures.py) generan PNG enriquecidos (per-scenario, ejes, radar, duración por fase, claims) y `benchmark_bundle.json` / `benchmark_table.md` bajo `docs/preprint/figures/`. Ver [`docs/preprint/README.md`](../../preprint/README.md).

---

### Extensión Plan v2 preprint (cerrada en repo; editorial abierta)

Alineado a [`ESTADO_PLAN_PREPRINT_V2.md`](../../ESTADO_PLAN_PREPRINT_V2.md):

- [x] `docs/PREPRINT_SKELETON.md` — claim, abstract con corchetes, tabla sección→artefacto.
- [x] `case_study_trace.json` automático en appendix + módulo `case_study_trace.py`.
- [x] Borrador inglés `docs/preprint/PREPRINT_DRAFT.md` con números de misión de referencia.
- [x] Figura de flujo case study + `benchmark_bundle` para material suplementario.
- [ ] Related work y venue finales (humano); réplica GPU completa del paper ancla (opcional, no requerida para el claim B+C honesto).

---

## Related work que ancla el paper (ya identificado)

Estos tres papers deben aparecer en la sección de Related Work y justifican el gap:

1. **PaperBench** (OpenAI, 2025. arXiv:2504.01848) — demuestra que replicación automatizada de papers ML es difícil y no resuelta. Justifica por qué infraestructura para esto es un gap real.

2. **MIB: Mechanistic Interpretability Benchmark** (2025. arXiv:2504.13151) — muestra que evaluación comparable en interpretabilidad requiere infraestructura estándar. El sistema propuesto es ese tipo de infraestructura para el proceso de investigación, no solo para los modelos.

3. **From Memorization to Reasoning in the Spectrum of Loss Curvature** (Merullo et al., 2025. arXiv:2510.24256) — candidato natural para el caso de uso safety (P2): conecta geometría interna del modelo con comportamiento observable. Paper con código, fenómeno bien estudiado, replicación alcanzable.

---

## Qué NO entra en este plan

| Idea tentadora | Por qué no |
|----------------|------------|
| Benchmark ML nuevo "para impresionar" | Desvía la misión y no está soportado por el claim |
| Estudio de usuarios con N participantes | Otro proyecto de investigación; Claim A vendrá después con datos reales |
| Segundo modelo LLM en el pipeline | Costo y scope; no es necesario para defender B+C |
| Generalizar el caso de uso a 5+ papers | Para el preprint inicial, uno bien documentado es más honesto que cinco superficiales |
| Autonomía completa del pipeline | Sigue marcada como parcial; forzarla arriesga estabilidad y honestidad del paper |
| Conectar con evaluación frontier models | Extensión natural, pero es otro paper; no inflar el scope inicial |

---

## Orden de ejecución

```
P-1 (claim clarity)
    ↓
P0 (artifacts anchor doc)  +  P1 (baseline agent_eval) — paralelo
    ↓
P2 (safety use case) — desbloquea el Claim C
    ↓
P3 (export appendix)  +  P4 (figura) — opcionales, bajo costo
    ↓
Draft del paper (sección por sección, en ese orden)
```

---

## Preguntas que un reviewer hostil haría — con respuestas honestas

**"¿Por qué debería usar esto en vez de LangChain + un script de evaluación?"**
Respuesta: porque el diseño es explícito sobre lo que garantiza (determinismo del harness, control de costos y secretos, auditabilidad del proceso) y lo que no (autonomía completa, generalización sin ajuste). LangChain no hace esas garantías porque no es su objetivo.

**"Un solo caso de uso en safety no demuestra que la arquitectura es general."**
Respuesta: correcto — y el paper no afirma generalidad empírica, afirma que el patrón de diseño es reutilizable. El caso de uso safety es evidencia de aplicabilidad, no prueba estadística de generalidad.

**"¿Cómo sé que los resultados del agent_eval son relevantes para mi caso de uso?"**
Respuesta: el harness es determinista y el baseline está versionado. La relevancia para un caso de uso específico requiere extender los escenarios — eso está documentado como trabajo futuro, no como limitación oculta.

---

## Checklist de cierre global

- [x] `docs/PREPRINT_CLAIM.md` existe con claim, abstract draft y preguntas hostiles respondidas
- [x] `docs/PREPRINT_ARTIFACTS.md` existe con tabla de cuatro columnas y límites explícitos
- [x] Baseline `agent_eval` en repo + test de regresión pasando en CI
- [x] `examples/safety_usecase/report.md` existe y es honesto sobre qué replicó y qué no
- [x] Related work identificado en el doc (los tres papers están referenciados en [PREPRINT_CLAIM.md](../../PREPRINT_CLAIM.md))
- [x] Ningún token ni dato sensible en artefactos exportados (`paper-export-appendix`: versión, git, harness JSON, pytest collect, traces, `benchmark_bundle.json`, `benchmark_table.md`)
- [x] `status-matrix.md` actualizado (appendix, benchmark bundle, safety use case)
- [x] Borrador de preprint en inglés con estructura del esqueleto + sección *Mentor briefing* — [`preprint/PREPRINT_DRAFT.md`](../../preprint/PREPRINT_DRAFT.md)
- [x] Síntesis para mentor y Plan v2 — [`actualizacion-31-3.md`](../../actualizacion-31-3.md)
- [ ] Pulir texto para envío (LaTeX / venue), citas formales en Related work, decisión de experimento opcional si un mentor lo pide

### Para pedir ayuda a un mentor

Leé y compartí [`actualizacion-31-3.md` §6](../../actualizacion-31-3.md) junto con [`preprint/PREPRINT_DRAFT.md`](../../preprint/PREPRINT_DRAFT.md) (sección *Mentor briefing*). Ahí están preguntas concretas de venue, claims y evaluación mínima.

**Plan v3 (evidencia cuantitativa):** [plan-v3-quantitative-reproducibility.md](plan-v3-quantitative-reproducibility.md), [REPRODUCIBILITY_NOTES.md](../../REPRODUCIBILITY_NOTES.md), [COMPARATIVE_TABLES.md](../../preprint/COMPARATIVE_TABLES.md).

---

*Estado técnico del preprint (artefactos, figuras, borrador base): cerrado en repo. Lo abierto es editorial, venue, segunda misión Plan v3 y posible experimento extra para credibilidad.*