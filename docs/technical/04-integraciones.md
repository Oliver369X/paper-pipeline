# 04 — Integraciones

## Perplexity

- Token: `PERPLEXITY_SESSION_TOKEN`.
- Cliente: `perplexity_webui_scraper` (Playwright / sesión).
- Modo un hilo: `single_thread_perplexity` + `run_state.json` (UUID de hilo).

## Notion

- `NOTION_TOKEN`, `notion_page_id` en la misión.
- `sync_sections` devuelve `SyncSectionsResult` (`ok`, `errors`).
- Triage tier 3: `NOTION_TRIAGE_PAGE_ID` vía `notion_telemetry`.

## Cursor CLI

- `CURSOR_API_KEY`, binario `agent` (opcional `CURSOR_AGENT_BIN`).
- Modo: **headless** — `agent -p --force --output-format text` (+ `CURSOR_AGENT_EXTRA_ARGS`); no es la CLI interactiva del IDE.
- Timeout: `CURSOR_CLI_TIMEOUT_SEC`.
- **Reintentos:** si un intento falla (exit ≠ 0), hasta `debugging.cursor_max_attempts` invocaciones; el siguiente prompt incluye stdout/stderr del fallo. Override: `CURSOR_CLI_MAX_ROUNDS`. Resumen: `outputs/cursor_cli_rounds.json`; trazas: `cursor_cli.log`, `cursor_cli_diagnostics.json`.
- Auditoría: cada invocación puede dejar en `outputs/run.log` un evento JSON `cursor_cli_subprocess_done` (`cwd`, `prompt_chars`, `duration_s`, `exit_code`, `timed_out`, `dry_run`, `attempt_index`, `attempts_total`, etc.) vía `PipelineLogger`.

## Experimento post-Cursor (opcional)

- Si `enable_experiment_runner`, `code_needed`, `enable_cursor_cli` y `experiment_runner.iteration_after_cursor: true`, el experimento integrado **no** corre en la fase **experiment_runner** temprana; tras un `cursor_cli` exitoso se ejecuta el bucle en `paper_pipeline/pipeline/experiment_iteration.py` (hasta `iteration_max_rounds`).
- **Validación determinista** de `metrics.json` (sin LLM): `outputs/validation/experiment_deterministic.json`; cotas opcionales `deterministic_metrics_bounds`.
- Tras fallo: `outputs/experiment_iteration_hint.md`, `experiment_iteration.jsonl`; si `iteration_perplexity_on_fail` y hay cupo, una pregunta corta a Perplexity. Detalle: [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md).
