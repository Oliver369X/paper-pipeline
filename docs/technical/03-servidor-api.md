# 03 — Servidor API

## Arranque

- **App:** `paper_pipeline.server.main:app`
- **CLI:** `paper-web` → uvicorn

## SPA (React)

Si existe `web/dist/`, la app monta `/assets` desde `dist/assets` y responde con `index.html` para rutas que no correspondan a un archivo bajo `dist` (excepto prefijos `api/…`, cubiertos por los routers). Así funcionan enlaces directos a `/missions/:id/cockpit` y similares sin 404 en el servidor.

## Routers

Todos los prefijos bajo **`/api/missions`** salvo que se indique otra base.

| Módulo | Rutas (resumen) |
|--------|-----------------|
| `missions_crud.py` | Lista, export TSV, crear, `PATCH` (bajo `/` y `/{mission_id}`). |
| `missions_runs.py` | `POST .../run`, SSE `.../events/{run_id}`, `run-log`, `events-log`, `run-state`. |
| `missions_content.py` | `draft`, `loop`, snapshots, `directive-history` y bridge mínimo de `goal` hacia el loop. |
| **`missions_cockpit.py`** | **Lectura** de artefactos en `outputs/` (ledger, evidencia, triaje, publicación, loop, métricas, safety, objective, memory, goal selection, goals, working memory, hipótesis, decisiones de agente, Perplexity strategy). |
| **`missions_brain.py`** | **Cerebro (Gemini):** chat, variantes, apply, historial — ver sección [Cerebro (Gemini)](#cerebro-gemini) más abajo. |

**Nota:** Crear misión y listar usan `POST /api/missions/` y `GET /api/missions/` (barra final) para compatibilidad con FastAPI al componer routers. El frontend (`web/`) usa estas rutas con `/` final.

## Cerebro (Gemini)

El **modelo** del cerebro no invoca herramientas: propone JSON (`mission`/`meta`, `brief_markdown`, opcional `cursor_checklist_markdown`) vía **Gemini**. El cliente puede **aplicar y arrancar el pipeline** con `POST .../brain/apply` y `run_pipeline: true` (mismo proceso que `POST .../run`; respuesta incluye `run_id` si aplica). El chat inyecta un extracto de `research_memory.jsonl` (límite `BRAIN_MAX_MEMORY_CONTEXT_CHARS`) y, si `BRAIN_USE_PERPLEXITY_CONTEXT`, un resumen Perplexity que incluye `paper_target` cuando figura en la misión. Requiere `GOOGLE_API_KEY` o `GEMINI_API_KEY` y `google-genai`; `GET /api/health` → `brain_gemini`: `configured` | `missing` | `missing_sdk`.

Base: **`/api/missions/{mission_id}/`**

| Método | Ruta | Comportamiento |
|--------|------|----------------|
| GET | `.../brain/history` | Mensajes desde `outputs/brain_chat_history.jsonl` (query `limit`, default 200). |
| DELETE | `.../brain/history` | Borra el historial de chat del cerebro. |
| POST | `.../brain/chat` | Body `{ "messages": [...] }`. Último mensaje = `user`. Append del turno al jsonl si OK. **503** si no hay API key Gemini. |
| POST | `.../brain/variants` | Body `{ "n": 1..10, "messages": [...] }`. Varias propuestas de misión. |
| POST | `.../brain/apply` | Body `{ "patch", "brief_markdown", "run_pipeline"?, "dry_run"? }`. Aplica misión y opcionalmente `outputs/brain_brief.md`; `research_memory` (`kind: brain_brief`). Si `run_pipeline: true`, tras aplicar arranca el pipeline (como `POST .../run`) y la respuesta incluye `run_id`. |

Variables y límites: ver `../.env.example` (`BRAIN_MODEL`, `BRAIN_MAX_HISTORY_MESSAGES`, `BRAIN_MAX_BRIEF_CHARS`, `BRAIN_USE_PERPLEXITY_CONTEXT` opcional con Perplexity).

Catálogo L1 inyectado en prompts: [`paper_pipeline/brain/brain_capabilities.md`](../../paper_pipeline/brain/brain_capabilities.md). Análisis OpenClaw vs producto: [brain-openclaw-gap.md](brain-openclaw-gap.md).

## Cockpit (artefactos del run)

Base: **`/api/missions/{mission_id}`** (mismo `mission_id` validado que el resto de la API).

| Método | Ruta | Artefacto / comportamiento |
|--------|------|----------------------------|
| `GET` | `.../ledger/latest` | `outputs/run_ledger.json` — **404** si no existe. |
| `GET` | `.../evidence/latest` | `outputs/evidence/evidence_index.json` — **404** si no existe. |
| `GET` | `.../claims/latest` | `outputs/evidence/claims.json` — **404** si no existe. |
| `GET` | `.../triage/latest` | `outputs/triage/triage_report.json` — **404** si no existe. |
| `POST` | `.../publish/preview` | Resumen `{ eligible, blocking_reasons? }`; si falta `publish_decision.json` devuelve `eligible: false` sin 404. |
| `GET` | `.../publish/decision` | JSON completo de `publication/publish_decision.json` — **404** si no existe. |
| `GET` | `.../loop/stop` | `outputs/loop/stop_decision.json` (p. ej. tras stall en `paper-loop`) — **404** si no existe. |
| `GET` | `.../metrics/validated` | `{ ok, errors }` vía `MetricsBundle` estricto — **404** si no hay `metrics.json`. |
| `GET` | `.../safety/latest` | Última línea válida de `outputs/safety_trace.jsonl` — **404** si no existe. |
| `GET` | `.../objective/latest` | JSON completo de `outputs/objective_state.json` — **404** si no existe. |
| `GET` | `.../memory/latest` | Última línea válida de `outputs/research_memory.jsonl` — **404** si no existe. |
| `GET` | `.../memory/index` | JSON completo de `outputs/memory_index.json` — **404** si no existe. |
| `GET` | `.../goal-selection/latest` | JSON completo de `outputs/goal_selection.json` — **404** si no existe. |
| `GET` | `.../goals/latest` | JSON de `outputs/goals.json` (árbol de metas V1) — **404** si no existe. |
| `GET` | `.../working-memory/latest` | JSON de `outputs/working_memory.json` — **404** si no existe. |
| `GET` | `.../hypotheses/latest` | JSON de `outputs/hypotheses_registry.json` — **404** si no existe. |
| `GET` | `.../agent/decisions/latest` | Última línea válida de `outputs/agent_decisions.jsonl` — **404** si no existe. |
| `GET` | `.../perplexity/calls/latest` | Última línea válida de `outputs/perplexity_call_record.jsonl` — **404** si no existe. |
| `GET` | `.../memory/query?goal_type=...&limit=...` | Entradas recientes de `research_memory.jsonl` cuyo `tags` o `payload.goal_type` coinciden con `goal_type`. |
| `POST` | `.../memory/compact` | Body `{ "dry_run": bool }`. Informe de compactación **sin borrar** JSONL en V1 (`compact_memory_dry_run`). |
| `POST` | `.../agent/run-step` | Body `{ "dry_run": bool }` (default `true`). Ejecuta `run_agent_step` sobre `outputs/` y **append** a `agent_decisions.jsonl`. |
| `POST` | `.../parallel/specs/generate` | Genera `outputs/parallel/specs_generated.json` desde `mission.md`. |

La página **Cockpit** en la web (`web/src/pages/CockpitPage.tsx`) consume ledger + evidence (obligatorios para la cabecera) y, en paralelo, publicación / triaje / loop / métricas / safety / objective / memory / goal selection / goals / working memory / hipótesis / última decisión de agente / última llamada Perplexity strategy (404 → sección vacía o mensaje, sin tumbar toda la vista).

## Bridge del loop

`POST /api/missions/{id}/loop` acepta ahora un `goal` opcional. Si no se envía, el backend intenta reutilizar `outputs/goal_selection.json`; si tampoco existe, cae al `DEFAULT_GOAL` actual del loop.

## Health

`GET /api/health` devuelve `status`, `version`, `perplexity_session`, `notion`, `brain_gemini` (sin llamadas lentas a APIs externas).

## `mission_id`

[`assert_safe_mission_id`](../../paper_pipeline/server/paths.py) rechaza `..`, `/`, `\` y caracteres fuera del patrón seguro.

## Ver también

- [OUTPUTS_REFERENCE.md](../OUTPUTS_REFERENCE.md) — qué archivos existen bajo `outputs/`.
- [HIPERVISOR_Y_PARALELO.md](../HIPERVISOR_Y_PARALELO.md) — triaje, `metrics.json`, `PAPER_PIPELINE_RELAX_METRICS`.
- [safety-policy-spec.md](safety-policy-spec.md) — política V1 de `SafetyController` y `safety_trace.jsonl`.
- [objective-spec.md](objective-spec.md) — fórmula y artefactos de `ObjectiveState V1`.
- [memory-spec.md](memory-spec.md) — contrato y límites de `ResearchMemory V1`.
- [goal-selection-spec.md](goal-selection-spec.md) — contrato y límites de `Goal Selection V1`.
- [goals-spec.md](goals-spec.md) — árbol `goals.json` y override de selección.
