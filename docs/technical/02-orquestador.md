# 02 — Orquestador

## Fases (orden actual, ver `_LEDGER_PHASES` en `runner.py`)

1. **mission_validation** — Contrato Pydantic + `validate_mission_contract` (`mission_version` 2 exige calidad activa).
2. **preflight** — Token/paths/binarios antes de Perplexity (`preflight_report.json`).
3. **perplexity_sections** — Secciones según `sections_needed`.
4. **assembly_draft** — `draft_paper.md` + README de código si aplica.
5. **experiment_runner** — Si `enable_experiment_runner`: benchmark integrado o `outputs/code/run_experiment.py`, → `metrics.json`. **Excepción:** con `experiment_runner.iteration_after_cursor: true` y `code_needed` + `enable_cursor_cli`, este paso se **omite** aquí y corre **después** de `cursor_cli` (bucle en `experiment_iteration.py`: experimento → validación determinista → reintentos Cursor opcionales; ver [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md)).
6. **quality_check** — Perplexity sobre el borrador si `enable_quality_check` y cupo; luego *quality gates* (`validation/quality_validation.json`).
7. **notion_sync** — API Notion si `enable_notion` y credenciales.
8. **cursor_cli** — Opcional si `code_needed` y `enable_cursor_cli` (headless `agent -p`; hasta `debugging.cursor_max_attempts` reintentos con contexto si falla; ver [04-integraciones.md](04-integraciones.md)).
9. **final_decision** — Evidence bundle + `publish_decision.json` + cierre del ledger.

Tras `enable_hypervisor_triage` (orquestador v2), el triaje puede ejecutarse **después** del pipeline; entonces se vuelve a escribir `publish_decision.json` y se fusiona `run_ledger.json` (`merge_ledger_after_triage`).

### Matriz tier × quality (publicación)

La función `compute_publish_signals` (`paper_pipeline/publication/signals.py`) combina `validation/quality_validation.json` y `triage/triage_report.json` sin red. Reglas útiles:

| Tier (triage) | `quality_validation.publishable` | Elegible |
|-----------------|-----------------------------------|----------|
| 3 | `true` | Sí (salvo otras razones de misión) |
| 3 | `false` | No — razón `tier3_without_quality_gates` |
| ≠3 | `true` | Sí si no hay otros bloqueos |

## Artefactos

| Archivo | Descripción |
|---------|-------------|
| `outputs/run_ledger.json` | **Ledger canónico** (`paper_pipeline/ledger`) |
| `outputs/run.log` | JSONL (`PipelineLogger`) |
| `outputs/pipeline_events.jsonl` | Eventos (`emit_event`) |
| `outputs/manifest.json` | `PipelineManifest` (compatibilidad UI; derivado del flujo) |

## Entrada

`run_pipeline(mission_path, dry_run=..., event_sink=...)` en [`paper_pipeline/pipeline/runner.py`](../../paper_pipeline/pipeline/runner.py).
