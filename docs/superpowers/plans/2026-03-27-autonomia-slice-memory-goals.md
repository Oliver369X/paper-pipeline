# Plan de ejecución — Slice C1 + D1 (memoria estratégica mínima + Goal Manager)

> **Objetivo:** Avanzar el [roadmap maestro](2026-03-26-autonomia-roadmap-maestro.md) con **dos entregas funcionales** encadenadas, cada una con tests obligatorios y docs.

---

## Slice C1 — Memoria estratégica mínima (V2 thin)

**Qué se entrega**

- `outputs/working_memory.json`: snapshot del ciclo (tipo de meta seleccionada, texto, observaciones recientes vacías en V1).
- `outputs/hypotheses_registry.json`: lista versionada de hipótesis (`open` \| `supported` \| `weakened` \| `rejected`); V1 puede arrancar vacía y solo `ensure` en cada paso.

**Código**

- Módulo dedicado (p. ej. `paper_pipeline/agent/strategic_memory.py`): modelos Pydantic, `save_working_memory`, `ensure_hypotheses_registry`, `update_strategic_memory_artifacts(output_dir, selection)`.
- Hook: llamado desde `update_goal_selection_artifacts` **después** de calcular `GoalSelection`.

**Tests**

- `tests/test_strategic_memory.py`: roundtrip JSON, contenido mínimo de `working_memory`.
- Extensión de `tests/test_pipeline_mocked.py`: existencia de archivos tras run mockeado.

**Docs**

- Ampliar `docs/technical/memory-spec.md` (sección V2 thin).
- `docs/OUTPUTS_REFERENCE.md`, `architecture/status-matrix.md`.

---

## Slice D1 — Goal Manager mínimo (`goals.json`)

**Qué se entrega**

- `outputs/goals.json`: documento versionado con nodos (`id`, `parent_id`, `description`, `goal_type`, `status`, `priority`).
- Si el archivo **no existe**, semilla automática **un** nodo raíz `pending` (literatura) usando el `topic` de `mission.md` si está disponible.
- Si existe un nodo `in_progress`, **`build_goal_selection_from_output_dir`** devuelve un `GoalSelection` alineado a ese nodo (override explícito antes de la heurística).

**Código**

- `paper_pipeline/agent/goals.py`: `GoalsDocument`, `GoalNode`, `ensure_goals_seed`, `load_goals_document`, `try_goal_override_from_tree`.
- `ensure_goals_seed` al inicio de `update_goal_selection_artifacts`.

**Tests**

- `tests/test_goals_manager.py`: seed, override `in_progress`, roundtrip.
- `tests/test_goal_selection.py`: caso override vs heurística.

**API + UI**

- `GET .../goals/latest`, `GET .../working-memory/latest`, `GET .../hypotheses/latest` en `missions_cockpit.py`.
- `CockpitPage.tsx`: tres `<details>` con JSON (patrón existente).
- `tests/test_server.py`: 404 sin archivo, 200 con fixture.

**Verificación global**

```bash
pytest -m "not integration and not notion_real" -q
```

---

## Orden de implementación

1. C1 (strategic_memory + hooks + tests + doc).
2. D1 (goals + override en `build_goal_selection` + API + UI + tests).

No editar este plan como parte del código; usar solo como referencia de alcance.
