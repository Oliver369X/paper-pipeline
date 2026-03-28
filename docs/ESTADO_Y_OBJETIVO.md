# Estado del paper-pipeline — dónde estamos y hacia dónde vamos

Documento vivo: resume el alcance del proyecto, lo ya implementado, límites conocidos y el objetivo final.

---

## Objetivo final

Construir un **pipeline de investigación orientado a paper** que:

1. Tome una **misión única** (`mission.md`: tema, venue, secciones, límites).
2. **Genere contenido** vía Perplexity (cliente web / sesión) en `outputs/*.md`, un **borrador** y opcionalmente **calidad** y **Notion**.
3. Permita **código y revisión iterativa** sin ser solo lineal: reglas en `.cursorrules`, salida en `outputs/cursor_turn.md`, instrucciones en `next_instruction.md`, con **`paper-loop`** para disparar **en cadena** llamadas reales a **Perplexity**, **Notion** y **Cursor CLI** según directivas `@…` en los markdown, más **meta-loop** (Perplexity revisor) y **watcher** opcional.
4. Ofrezca **automatización opcional del agente de código** (`paper-cursor-agent` / `enable_cursor_cli` en la misión) y el **bucle reactivo** `paper-loop` como **camino principal “real”** frente a la demo visual.
5. Incluya **tests**: unitarios (rápidos, algunos con mocks solo para no depender de red en CI), **integración** opcional con Perplexity/Cursor real, y E2E **solo** de la UI demo (`visual-flow`) con Playwright.

En una frase: **reducir el cuello de botella humano en la parte repetible (investigación + borrador + bucle de instrucciones y llamadas cruzadas), manteniendo control explícito sobre costes, secretos y pasos opcionales.**

### Rigor científico y honestidad de producto

- El flujo **lineal Perplexity → secciones → borrador** es **modo narrativo**; no demuestra por sí solo agentes autónomos con herramientas, baselines ni números reproducibles. Ver [MODE_NARRATIVE_VS_EMPIRICAL.md](MODE_NARRATIVE_VS_EMPIRICAL.md).
- **Alineá** el `paper_target` / referencias arXiv con el paper real: [ARXIV_TARGET_ALIGNMENT.md](ARXIV_TARGET_ALIGNMENT.md) (ej.: arXiv:2410.02159 es memorización en LMs, no «agentes autónomos» genéricos).
- Capas de evaluación y checklist de claims: [technical/EVALUATION_LAYERS.md](technical/EVALUATION_LAYERS.md), baselines: [BASELINES_AND_METRICS_TEMPLATE.md](BASELINES_AND_METRICS_TEMPLATE.md), MVP métricas: [technical/MVP_BENCHMARK.md](technical/MVP_BENCHMARK.md), roadmap agentes: [technical/ROADMAP_MULTI_AGENT.md](technical/ROADMAP_MULTI_AGENT.md).

---

## Dónde estamos ahora

| Capa | Estado |
|------|--------|
| Parser de misión (`mission.md`) | Listo |
| Orquestador lineal Perplexity + `draft_paper.md` + **experiment_runner** (opc.) + quality + Notion + Cursor CLI opcional + **bucle experimento post-Cursor** (`iteration_after_cursor`) | Listo |
| **Bucle reactivo `paper-loop`** (`@PERPLEXITY` / `@NOTION` / `@CURSOR` + meta-loop) | Listo |
| Meta-loop + `paper-meta-watch` | Listo |
| Cursor CLI (`paper-cursor-agent`, `enable_cursor_cli`; reintentos headless; validación determinista de métricas en bucle post-Cursor) | Listo (opt-in) |
| Demo visual `visual-flow` (sin APIs) | Listo — **solo diagrama / enseñanza** |
| `paper-record-visual` + E2E Playwright con vídeo opcional | Listo (prueba la demo HTML, no el pipeline) |
| CI GitHub + job Cursor opcional apagado | Listo |
| Venv / Docker documentados | Listo |
| API **cockpit** (`/api/missions/{id}/ledger|evidence|triage|publish|loop|metrics`) + página web Cockpit | Listo (ver [technical/03-servidor-api.md](technical/03-servidor-api.md)) |
| Ledger post-triage, señales de publicación, `loop_state` / `stop_decision`, packs opcionales | Listo (ver [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md), plan en `docs/superpowers/plans/`) |
| Safety controller V1 + `safety_trace.jsonl` | Listo |
| Objective State V1 (`objective_state.json`, `objective_trace.jsonl`, cockpit API) | Listo |
| ResearchMemory V1 (`research_memory.jsonl`, `memory_index.json`, cockpit API) | Listo |
| Goal Selection V1 (`goal_selection.json`, cockpit API, bridge mínimo al loop) | Listo |
| Modo `autonomy` en `mission.md`, scheduler `run_agent_step`, `agent_decisions.jsonl`, API `POST .../agent/run-step`, política pre/post mínima | Listo (ejecución real del pipeline tras paso autónomo aún no cableada; ver `.env.example` `PAPER_PIPELINE_AUTONOMY_EXECUTE`) |

---

## Qué tenemos (artefactos clave)

- **Entrada:** `mission.md`.
- **Salida típica:** `outputs/<sección>.md`, `draft_paper.md`, `metrics.json` si experiment runner, `validation/experiment_deterministic.json` si bucle post-Cursor, `quality_gaps.md`, `notion_sync.log`, `outputs/code/README.md` si `code_needed`, `cursor_cli_rounds.json` / `experiment_iteration.jsonl` si aplica.
- **Bucle:** `paper-loop mission.md` lee directivas en `cursor_turn.md` / `next_instruction.md`, ejecuta APIs reales, actualiza borrador y puede lanzar meta-loop.
- **Cursor:** `cursor_turn.md`, `next_instruction.md`, `cursor_cli.log` si aplica.
- **CLI:** ver inventario completo en [technical/07-inventario-cli-y-entorno.md](technical/07-inventario-cli-y-entorno.md) — incluye `paper-web`, `paper-parallel`, `paper-racing-loop`, `paper-agent-step`, `paper-report-figures`, además de `paper-pipeline`, `paper-loop`, `paper-meta-loop`, `paper-meta-watch`, `paper-record-visual`, `paper-cursor-agent`.
- **Config:** `.env` con `PERPLEXITY_SESSION_TOKEN`; opcional `CURSOR_API_KEY`, Notion, etc.

---

## Hacia dónde vamos (mejoras opcionales)

- Afinar plantillas y convenciones de `@PERPLEXITY:sección` según venues.
- Más automatización en CI solo donde haya secretos y binarios disponibles.
- Mantener al día la doc oficial del CLI Cursor (`agent`).

---

## Limitaciones

1. **Perplexity:** sesión que **caduca**.
2. **Cursor CLI:** instalación aparte + `CURSOR_API_KEY`; en Docker/CI a menudo falta `agent` en PATH.
3. **`--force`:** puede **modificar** el repo; backup/commit antes de automatizar.
4. **Coste** de APIs.
5. **Automations** cloud de Cursor: **fuera** de este repo.
6. **`visual-flow`:** no ejecuta Perplexity; el flujo **real** es terminal (`paper-pipeline`, `paper-loop`).

---

## Qué está probado

| Qué | Cómo |
|-----|------|
| Directivas `@PERPLEXITY` / `@NOTION` / `@CURSOR` | `test_loop_directives.py` (parser, sin red) |
| Orquestador / meta / Cursor CLI | Tests con mocks de cliente (CI sin claves) |
| Perplexity real | `pytest -m integration` + `test_perplexity_integration` |
| Notion real (opcional) | `pytest -m notion_real` (token; ver `test_notion_smoke_optional`) |
| CLI `agent` | `test_cursor_cli_integration` si hay key + binario |
| Demo HTML | `pytest -m e2e` (Playwright) |

**Suite local habitual (sin cuota de APIs):** `pytest -m "not integration and not notion_real" -q`.

**Validación “real” recomendada:** `.env` + `paper-pipeline mission.md` y/o `paper-loop mission.md` con directivas de prueba.

---

## Cómo leer este documento

- **Uso diario:** README del repo y `.env.example`.
- **Visión de alcance:** este archivo.
- **Mapa de toda la documentación:** [docs/README.md](README.md).

---

*Última actualización: índice `docs/README.md`, marcadores `notion_real` + `integration`, API web y eventos de pipeline.*
