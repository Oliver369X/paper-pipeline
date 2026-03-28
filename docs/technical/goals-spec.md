# Goal Manager V1 — `goals.json`

## Objetivo

Persistir un **árbol de metas** explícito por misión. Si existe un nodo con `status: "in_progress"`, `build_goal_selection_from_output_dir` **prioriza** ese nodo sobre la heurística de `GoalSelector`.

## Formato

- `version`: entero (1).
- `mission_topic_hint`: texto informativo (semilla).
- `nodes`: lista de nodos con:
  - `id`, `parent_id` (opcional)
  - `description`
  - `goal_type`: uno de `literature` \| `verification` \| `writing` \| `experiment` \| `wait_human` \| `stop`
  - `status`: `pending` \| `in_progress` \| `done` \| `abandoned`
  - `priority` ∈ [0, 1]
  - `source_artifacts` (opcional)

## Semilla automática

Si `goals.json` no existe, `ensure_goals_seed` crea un único nodo `pending` de tipo `literature` usando el `topic` de `mission.md` (si es legible).

## API

- `GET /api/missions/{id}/goals/latest`

## Verificación

```bash
pytest tests/test_goals_manager.py tests/test_goal_selection.py -q
```
