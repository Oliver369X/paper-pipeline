# Artefactos del preprint (paper sobre **paper-pipeline**)

Documento ancla para redactar la sección *Artifacts* / *Methods* de un manuscrito que describe el sistema **paper-pipeline**, y para que revisores reproduzcan claims técnicos sin adivinar rutas. No sustituye la especificación completa del harness: ver [technical/agent-eval-spec.md](technical/agent-eval-spec.md).

---

## Tabla: afirmación → artefacto → comando → limitación

| Afirmación del paper (ejemplo) | Artefacto en el repo | Ruta / comando | Limitación honesta |
|--------------------------------|----------------------|----------------|--------------------|
| Gobernanza y selección de metas comprobables en CI sin LLM | Harness `agent_eval` (oráculos deterministas) | `python -m paper_pipeline.agent_eval` o `python -m paper_pipeline.agent_eval --out /tmp/report.json` | Escenarios **sintéticos** versionados; no miden desempeño en producción ni calidad de texto de Perplexity |
| Regresión explícita del harness frente a un baseline fijado | Baseline JSON | [examples/baselines/agent_eval_baseline.json](../examples/baselines/agent_eval_baseline.json) | Umbrales y lista de `expected_scenario_ids` las fija el proyecto; cualquier cambio de escenario exige actualizar el baseline y el PR |
| Comprobación local del baseline (exit 0/1) | Mismo baseline + CLI | `python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json` o, desde la raíz del repo, `paper-agent-eval-check` | Requiere ejecutarse con el cwd correcto para el wrapper por defecto; ver [examples/baselines/README.md](../examples/baselines/README.md) |
| Cobertura declarada de componentes (ledger, triaje, API, etc.) | Matriz viva | [architecture/status-matrix.md](architecture/status-matrix.md) | Es inventario de implementación, no certificación externa |
| Figuras tipo “métrica principal vs baseline” a partir de `outputs/metrics.json` | CLI de informes | `paper-report-figures` (extra `figures`) — ver [FLUJO_REAL_SOTA_FIGURES.md](FLUJO_REAL_SOTA_FIGURES.md) | Solo aplica si el manuscrito incluye un ejemplo con métricas reales en disco; no es obligatorio para defender solo el harness |
| Aplicabilidad a investigación “trustworthy” / memorización (Claim C, plan [mio.md](superpowers/plans/mio.md)) | Caso de uso P2 versionado | [examples/safety_usecase/report.md](../examples/safety_usecase/report.md), `python scripts/safety_usecase_repro.py`, `pytest tests/test_safety_usecase_repro.py` | Un solo ancla (arXiv:2510.24256); **no** réplica GPU ni run Perplexity en CI; claims del fixture son ilustrativos |
| Bundle mínimo para anexo / material suplementario | Exportación local | `paper-export-appendix -o /ruta/bundle` (desde raíz del repo; opcional `--repo-root`, `--case-study-outputs DIR`) | Incluye **`case_study_trace.json`**, **`benchmark_bundle.json`**, **`benchmark_table.md`** (mismo `agent_eval` que el JSON del harness; sin segunda corrida del harness). No incluye `.env` ni tokens; `git_commit` puede ser `unknown` fuera de git |
| Tabla “benchmark” reproducible (harness + tiempos de fase) | `benchmark_bundle.json` | `python -m paper_pipeline.reporting.benchmark_bundle -o ruta.json` o `python scripts/generate_preprint_figures.py` (también escribe PNG) | **No** es benchmark de precisión ML; agrega `agent_eval` por escenario + `case_study_trace` + duraciones de fase del ledger |
| Plan v3: notas de reproducibilidad y tablas A vs B | [`REPRODUCIBILITY_NOTES.md`](REPRODUCIBILITY_NOTES.md), [`preprint/COMPARATIVE_TABLES.md`](preprint/COMPARATIVE_TABLES.md) | `python scripts/audit_abstract_numbers.py` (Markdown en stdout) | Números de misión = **snapshot**; ver columnas “Reproducibility class” en notas |
| Plan v3 (plan canónico) | [`superpowers/plans/plan-v3-quantitative-reproducibility.md`](superpowers/plans/plan-v3-quantitative-reproducibility.md) | — | Fase 2 (segunda misión) puede quedar pendiente en el repo |
| Traza de caso de estudio para revisores (ledger, triaje, métricas, conteo de claims) | `case_study_trace.json` (dentro del bundle) | Generado por `paper-export-appendix`; por defecto usa `data/missions/4f6715a65f4c/outputs` si existe `run_ledger.json` | Es **resumen redactado**, no volcado bruto de logs; no sustituye inspección de `run_ledger.json` si el revisor lo pide |
| Figuras de arquitectura (LaTeX / slides) | Fuentes Mermaid + scripts | [`docs/assets/README.md`](assets/README.md), `scripts/export_architecture_figure.ps1` / `.sh` | Requiere `@mermaid-js/mermaid-cli` (`mmdc`); PNG generados en `docs/assets/generated/` (opcional en git) |

---

## Claims y abstract (redacción del manuscrito)

- [PREPRINT_CLAIM.md](PREPRINT_CLAIM.md) — qué afirma el paper (B+C), qué **no** afirma, borrador de abstract, related work ancla.
- [PREPRINT_SKELETON.md](PREPRINT_SKELETON.md) — claim en una frase, abstract con corchetes y números de referencia, tabla sección ↔ artefacto.
- [preprint/PREPRINT_DRAFT.md](preprint/PREPRINT_DRAFT.md) — **borrador completo en inglés** (Intro–Conclusión + apéndices conceptuales) alineado a artefactos actuales; no es envío a arXiv hasta revisión humana.

---

## Qué no demuestra este repositorio

- El modo **narrativo** (Perplexity → secciones → borrador) **no** demuestra por sí solo experimentos ejecutados ni números reproducibles frente a un paper objetivo: ver [MODE_NARRATIVE_VS_EMPIRICAL.md](MODE_NARRATIVE_VS_EMPIRICAL.md).
- La revisión asistida (`quality_check`) y las capas de [EVALUATION_LAYERS.md](technical/EVALUATION_LAYERS.md) **no** son revisión por pares ni verificación empírica independiente de claims científicos.
- El baseline de `agent_eval` fija **comportamiento de oráculos internos** (safety, goal selection, integridad de rutas), **no** métricas de un modelo entrenado ni “SOTA” en una tarea ML.
- `paper-agent-eval-check` y los tests asociados **no** requieren red ni claves; por tanto **no** validan integración con Perplexity, Notion ni Cursor.
- La matriz de arquitectura puede quedar desactualizada si no se actualiza tras un cambio de contrato; la fuente normativa de comportamiento sigue siendo código + tests.

---

## Verificación rápida (revisor)

Desde la raíz del repo `paper-pipeline`, con el entorno de desarrollo instalado (`pip install -e ".[dev]"`):

```bash
pytest tests/test_agent_eval_runner.py tests/test_agent_eval_baseline.py tests/test_safety_usecase_repro.py tests/test_appendix_export.py tests/test_case_study_trace.py tests/test_benchmark_bundle.py tests/test_preprint_figures.py tests/test_audit_abstract_numbers.py tests/test_docs_assets.py -q
python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json
```

Salida esperada del segundo comando: mensaje `agent_eval: baseline check passed` en stderr y código de salida `0`.

Suite local habitual sin APIs externas (más amplia):

```bash
pytest -m "not integration and not notion_real" -q
```

---

## Especificación normativa del harness

- [technical/agent-eval-spec.md](technical/agent-eval-spec.md) — escenarios, métricas del scorecard, política de baseline versionado.

---

**Paquete listo para incluir en el manuscrito (figuras PNG + snapshot):** [preprint/README.md](preprint/README.md).

*Alineado al plan [superpowers/plans/mio.md](superpowers/plans/mio.md) (P0, P3, P4).*
