# Goal Selection V1

Documento técnico de la primera capa de selección explícita del siguiente paso de investigación.

## Objetivo

Persistir una recomendación estructurada en `outputs/goal_selection.json` usando como insumos:

- `objective_state.json`
- `memory_index.json`
- artefactos derivados del run actual

Esta V1 no implementa `goals.json`, árbol de metas ni scheduler autónomo. Solo recomienda el siguiente tipo de acción y deja trazabilidad suficiente para depuración y supervisión humana.

## Campos de `goal_selection.json`

- `version`
- `selected_goal_type`
  - `literature`
  - `verification`
  - `writing`
  - `experiment`
  - `wait_human`
  - `stop`
- `goal_text`
- `priority`
- `reason`
- `source_signals`
- `gates`
- `last_updated_at`

## Reglas V1

- `loop_stopped == true` → `wait_human`
- `requires_human_approval == true` → `wait_human`
- estado bloqueado o publicación bloqueada reciente → `verification`
- publicación elegible con contribución alta → `writing`
- estado sano con contribución positiva pero sin publicación lista → `experiment`
- fallback → `literature`

## Hooks implementados

- `paper_pipeline/pipeline/runner.py`
  - selección post-pipeline
- `paper_pipeline/orchestrator_v2.py`
  - selección post-hypervisor
- `paper_pipeline/integrated_loop_main.py`
  - selección tras `loop_stop`

## Bridge mínimo con el loop

`LoopRequest` admite ahora un campo opcional `goal`.

Regla V1:

- si `goal` explícito viene en el request, se usa ese
- si no viene, `missions_content.py` intenta leer `outputs/goal_selection.json`
- si no existe, cae al `DEFAULT_GOAL` del loop actual

Esto mantiene compatibilidad con el flujo manual existente.

## API y Cockpit

- `GET /api/missions/{id}/goal-selection/latest`
- bloque `Goal Selection` en `CockpitPage`

## Verificación recomendada

```bash
pytest tests/test_goal_selection.py -q
pytest tests/test_server.py -q
pytest -m "not integration and not notion_real" -q
```

