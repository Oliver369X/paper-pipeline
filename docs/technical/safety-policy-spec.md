# Safety Policy Spec V1

Documento técnico para la primera capa explícita de control jerárquico del modo autónomo.

## Objetivo

Definir una política pequeña, auditable y no generativa que traduzca señales ya existentes del repo a decisiones de gobernanza:

- `ALLOW`
- `ALLOW_WITH_RESTRICTIONS`
- `REQUIRE_HUMAN_APPROVAL`
- `BLOCK`

La meta de V1 no es seleccionar goals ni optimizar utilidad, sino dejar trazabilidad clara de cuándo un paso debe bloquearse o escalarse a revisión humana.

## Fuentes de verdad que consume

- `outputs/triage/triage_report.json`
- `outputs/publication/publish_decision.json`
- `outputs/loop/stop_decision.json`
- `outputs/run_ledger.json`

El controlador **no** recomputa quality, triage ni publish; consume esas señales.

## Reglas V1

### `BLOCK`

Se usa cuando hay una restricción dura ya disparada en el sistema.

Casos implementados:

- `invalid_metrics_block_publish`
  - Acción candidata: `publish_consolidation`
  - Se activa si existen `metrics_validation_errors`
- `publish_blocking_reasons`
  - Acción candidata: `publish_consolidation`
  - Se activa si `publish_decision.json` ya contiene `blocking_reasons`
- `loop_stop_decision`
  - Acción candidata: `loop_iteration`
  - Se activa cuando `paper-loop` emitió una parada por stall
- `invalid_metrics_block_agent_step`
  - Acción candidata: `agent_step`
  - Se activa si `triage_report.json` lista `metrics_validation_errors` (o errores estrictos equivalentes) consumidos vía `SafetyContext`
- `loop_stop_blocks_agent_step`
  - Acción candidata: `agent_step`
  - Se activa si `objective_state.json` indica parada de bucle (`gates.loop_stopped`) mapeada a razones de loop

### Política pre/post (scheduler)

Además del `SafetyController`, el scheduler llama a funciones puras en `paper_pipeline/agent/safety_policy.py`:

- `policy_check_pre_goal(output_dir, selected_goal_type=...)` — bloquea autonomía si el triaje reporta métricas inválidas (`triage/triage_report.json`).
- `policy_check_post_action(output_dir, dry_run=...)` — en V1, `dry_run=true` siempre permite; post real queda reservado para comprobaciones futuras.

### `REQUIRE_HUMAN_APPROVAL`

Se usa cuando el sistema detecta una situación sensible que no debe promocionarse automáticamente.

Caso implementado:

- `breakthrough_requires_human_approval`
  - Acción candidata: `publish_consolidation`
  - Se activa si `triage_tier == 3` y el run sigue siendo elegible para publicación

### `ALLOW`

Se usa cuando no hay gates rojos ni señales que exijan intervención humana.

Caso implementado:

- `allow_default`

### `ALLOW_WITH_RESTRICTIONS`

Reservado para pasos futuros. En V1 el controlador define el enum, pero los hooks implementados hoy usan `ALLOW`, `REQUIRE_HUMAN_APPROVAL` o `BLOCK`.

## Artefacto de auditoría

Archivo: `outputs/safety_trace.jsonl`

Formato por línea:

```json
{
  "ts": "2026-03-26T00:00:00+00:00",
  "candidate_action": "publish_consolidation",
  "decision": "REQUIRE_HUMAN_APPROVAL",
  "rule_id": "breakthrough_requires_human_approval",
  "reasons": ["Breakthrough-tier publication requires explicit human approval."],
  "source_artifacts": [
    "publication/publish_decision.json",
    "triage/triage_report.json"
  ],
  "mission_id": null,
  "run_id": null
}
```

## Hooks V1

- `paper_pipeline/publication/publish_manager.py`
  - Evalúa safety al escribir `publish_decision.json`
- `paper_pipeline/integrated_loop_main.py`
  - Registra bloqueo al emitir `stop_decision.json`
- `paper_pipeline/orchestrator_v2.py`
  - Añade una traza post-triage mínima

## Consumo en API / web

- API: `GET /api/missions/{id}/safety/latest`
- UI: bloque “Safety” en `CockpitPage`

## Comandos de verificación recomendados

```bash
pytest tests/test_safety_controller.py tests/test_safety_policy.py -q
pytest tests/test_publication_signals.py tests/test_integrated_loop_stop.py tests/test_server.py -q
pytest -m "not integration and not notion_real"
```

