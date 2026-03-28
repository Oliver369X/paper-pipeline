# Research Memory V1

Documento técnico de la primera memoria episódica mínima para `paper-pipeline`.

## Objetivo

Persistir eventos de investigación de alto valor en:

- `outputs/research_memory.jsonl`
- `outputs/memory_index.json`

La meta de V1 no es ofrecer retrieval híbrido, lessons consolidadas ni registro de hipótesis. Solo deja una capa append-only y un índice barato para inspección humana y futura automatización.

## Alcance V1

### Sí entra

- Eventos `quality`
- Eventos `triage`
- Eventos `publish`
- Eventos `loop_stop`
- Eventos `run_consolidation`
- Lectura cockpit por API

### Helpers y API (V1 ligero)

- `query_memory_entries_for_goal(output_dir, goal_type, limit)` — filtra líneas recientes por `tags` o `payload.goal_type`.
- `compact_memory_dry_run(output_dir)` — informe sin borrar ni fusionar entradas (planificación).
- API: `GET .../memory/query`, `POST .../memory/compact` (ver [03-servidor-api.md](03-servidor-api.md)).

### No entra (aún)

- `lessons_learned.md` (generado)
- promotion / archival avanzada real sobre JSONL

## V2 thin — working memory + registro de hipótesis

Además de V1, el pipeline puede escribir:

- `outputs/working_memory.json` — snapshot del último `GoalSelection` (tipo, texto, razón) para el ciclo actual.
- `outputs/hypotheses_registry.json` — lista versionada de hipótesis (`open` \| `supported` \| `weakened` \| `rejected`); en la primera versión puede estar **vacía** y solo asegurarse en cada paso.

Se actualizan desde `update_goal_selection_artifacts` (tras `goal_selection.json`). Ver plan [../superpowers/plans/2026-03-27-autonomia-slice-memory-goals.md](../superpowers/plans/2026-03-27-autonomia-slice-memory-goals.md).

## Formato de `research_memory.jsonl`

Cada línea es un objeto JSON con:

- `ts`
- `memory_id`
- `kind`
- `mission_id`
- `run_id`
- `summary`
- `confidence`
- `source_artifacts`
- `tags`
- `payload`

Ejemplo:

```json
{
  "ts": "2026-03-26T00:00:00+00:00",
  "memory_id": "abc123def456",
  "kind": "publish",
  "mission_id": null,
  "run_id": null,
  "summary": "Publish elegible",
  "confidence": 0.8,
  "source_artifacts": [
    "publication/publish_decision.json",
    "triage/triage_report.json"
  ],
  "tags": ["publish", "tier2"],
  "payload": {
    "eligible_for_publication": true
  }
}
```

## Formato de `memory_index.json`

- `version`
- `counts_by_kind`
- `last_event`
- `latest_by_kind`
- `source_artifacts`
- `last_updated_at`

Es un resumen barato para Cockpit. Debe poder regenerarse desde `research_memory.jsonl`.

## Hooks implementados

- `paper_pipeline/agent/goal_selection.py` (`update_goal_selection_artifacts`)
  - `working_memory.json`, `hypotheses_registry.json` (ensure vacío si aplica)
- `paper_pipeline/pipeline/runner.py`
  - `quality`
  - `run_consolidation`
- `paper_pipeline/hypervisor/triage.py`
  - `triage`
- `paper_pipeline/publication/publish_manager.py`
  - `publish`
- `paper_pipeline/integrated_loop_main.py`
  - `loop_stop`
- `paper_pipeline/orchestrator_v2.py`
  - consolidación adicional post-hypervisor

## API y Cockpit

- `GET /api/missions/{id}/memory/latest`
- `GET /api/missions/{id}/memory/index`
- `GET /api/missions/{id}/memory/query?goal_type=...`
- `POST /api/missions/{id}/memory/compact`
- `GET /api/missions/{id}/working-memory/latest`
- `GET /api/missions/{id}/hypotheses/latest`

La UI los muestra en bloques `Memory`, `Working memory` e `Hipótesis` en `CockpitPage`.

## Verificación recomendada

```bash
pytest tests/test_research_memory.py -q
pytest tests/test_server.py -q
pytest -m "not integration and not notion_real" -q
```

