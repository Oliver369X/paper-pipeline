# Objective State V1

Documento técnico de la primera capa explícita de función objetivo auditable para `paper-pipeline`.

## Objetivo

Persistir un estado derivado en `outputs/objective_state.json` y una traza append-only en `outputs/objective_trace.jsonl` usando únicamente artefactos ya existentes del sistema:

- `validation/quality_validation.json`
- `triage/triage_report.json`
- `publication/publish_decision.json`
- `run_ledger.json`
- `loop/stop_decision.json`
- `safety_trace.jsonl`

Esta V1 **no** selecciona goals ni ejecuta autonomía plena. Solo consolida señales del run actual para dejar una base auditable sobre la que luego pueda construirse Goal Manager, scheduler y memoria estratégica.

## Campos de `objective_state.json`

- `version`
- `root_objective`
- `status`
  - `healthy`
  - `blocked`
  - `stalled`
  - `needs_review`
- `utility_total`
- `terms`
  - `contribution_estimate`
  - `quality_score`
  - `cost_score`
  - `risk_score`
  - `coherence_score`
- `gates`
  - `metrics_valid`
  - `publishable`
  - `loop_stopped`
  - `requires_human_approval`
- `source_artifacts`
- `last_updated_at`

## Campos de `objective_trace.jsonl`

- `ts`
- `candidate_action_family`
- `utility_total`
- `terms`
- `gates`
- `decision_summary`
- `source_artifacts`

## Reglas V1

### `contribution_estimate`

Se deriva del `triage_tier`:

- tier 3 → contribución alta
- tier 2 → contribución moderada
- tier 1 / 0 → contribución negativa o débil

### `quality_score`

Se deriva de `quality_validation.publishable` y de `blocking_reasons`.

### `cost_score`

V1 usa proxies baratos y observables:

- número de fases en `run_ledger`
- penalización extra si hubo `loop_stop`

### `risk_score`

Penaliza:

- `blocking_reasons`
- `metrics_validation_errors`
- `metrics_relax_mode`
- `REQUIRE_HUMAN_APPROVAL` en `safety_trace`

### `coherence_score`

Penaliza contradicciones claras entre señales, por ejemplo:

- publicación elegible con `tier == 0`
- loop parado por stall
- `publishable == true` coexistiendo con bloqueos explícitos

## Fórmula V1

La utilidad total es deliberadamente pequeña y auditable:

```text
utility_total = contribution_estimate + quality_score + coherence_score - cost_score - risk_score
```

No intenta ser la función objetivo final del modo autónomo; sirve como consolidación mínima y base de debugging.

## Hooks implementados

- `paper_pipeline/pipeline/runner.py`
  - al final del pipeline v1 exitoso
- `paper_pipeline/orchestrator_v2.py`
  - después de triage + publish + merge ledger
- `paper_pipeline/integrated_loop_main.py`
  - al escribir `loop/stop_decision.json`

## API y cockpit

- API: `GET /api/missions/{id}/objective/latest`
- UI: bloque “Objective” en `CockpitPage`

## Verificación recomendada

```bash
pytest tests/test_objective_state.py -q
pytest tests/test_server.py -q
pytest -m "not integration and not notion_real" -q
```

