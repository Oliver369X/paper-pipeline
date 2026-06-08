# 04 — Integraciones

## Perplexity

- Token: `PERPLEXITY_SESSION_TOKEN`.
- Cliente: `perplexity_webui_scraper` (Playwright / sesión).
- Modo un hilo: `single_thread_perplexity` + `run_state.json` (UUID de hilo).

## Notion

- `NOTION_TOKEN`, `notion_page_id` en la misión.
- `sync_sections` devuelve `SyncSectionsResult` (`ok`, `errors`).
- Triage tier 3: `NOTION_TRIAGE_PAGE_ID` vía `notion_telemetry`.

## Cursor agent (SDK default, CLI fallback)

- `CURSOR_API_KEY` obligatoria.
- **Backend SDK (default):** `cursor-sdk` con `CURSOR_AGENT_MODEL=composer-2.5`, runtime local (`LocalAgentOptions.cwd`). Sin binario `agent` en PATH. Resume: `outputs/cursor_agent_state.json` + `CURSOR_AGENT_RESUME=1`. En Windows, `paper_pipeline/cursor_sdk_bridge_patch.py` parchea el arranque del bridge (``select`` en pipes no es válido en Win32).
- **Backend CLI:** `CURSOR_AGENT_BACKEND=cli` — subprocess `agent -p --force --output-format text` (+ `CURSOR_AGENT_EXTRA_ARGS`); binario vía PATH o `CURSOR_AGENT_BIN`.
- Timeout: `CURSOR_CLI_TIMEOUT_SEC` (ambos backends).
- **Reintentos:** hasta `debugging.cursor_max_attempts` (override `CURSOR_CLI_MAX_ROUNDS`). SDK reutiliza el mismo agente con `send()`; CLI respawnea con prompt de follow-up. Resumen: `outputs/cursor_cli_rounds.json`; trazas: `cursor_cli.log`, `cursor_cli_diagnostics.json` (incluye `backend`, `model`, `run_id`, `agent_id` en SDK).
- Auditoría: evento `cursor_cli_subprocess_done` en `run.log` (`backend`, `run_id`, `agent_id`, `model`, …) vía `PipelineLogger`.

## Experimento post-Cursor (opcional)

- Si `enable_experiment_runner`, `code_needed`, `enable_cursor_cli` y `experiment_runner.iteration_after_cursor: true`, el experimento integrado **no** corre en la fase **experiment_runner** temprana; tras un `cursor_cli` exitoso se ejecuta el bucle en `paper_pipeline/pipeline/experiment_iteration.py` (hasta `iteration_max_rounds`).
- **Validación determinista** de `metrics.json` (sin LLM): `outputs/validation/experiment_deterministic.json`; cotas opcionales `deterministic_metrics_bounds`.
- Tras fallo: `outputs/experiment_iteration_hint.md`, `experiment_iteration.jsonl`; si `iteration_perplexity_on_fail` y hay cupo, una pregunta corta a Perplexity. Detalle: [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md).
