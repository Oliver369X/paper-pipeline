# 07 — Inventario de CLIs, extras pip y entorno

Documento de **referencia exhaustiva** (complementa [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md) y [`.env.example`](../../.env.example)). Los puntos de entrada salen de [`pyproject.toml`](../../pyproject.toml) (`[project.scripts]`).

## Comandos instalados (`pip install -e .`)

| Comando | Módulo de entrada | Rol breve |
|---------|-------------------|-----------|
| `paper-pipeline` | `paper_pipeline.__main__:main` | Pipeline lineal: Perplexity → borrador → experiment_runner (opc.; aplazable si `iteration_after_cursor`) → quality → Notion → Cursor CLI (opc.; reintentos headless) → bucle experimento post-Cursor si aplica. |
| `paper-meta-loop` | `paper_pipeline.meta_main:main` | Una ronda de meta-revisor Perplexity → `next_instruction.md`. |
| `paper-meta-watch` | `paper_pipeline.meta_watch:main` | Igual, disparado al guardar `cursor_turn.md` (polling + debounce). |
| `paper-record-visual` | `paper_pipeline.record_visual:main` | Graba interacción con la demo HTML `visual-flow` (Playwright). |
| `paper-cursor-agent` | `paper_pipeline.cursor_cli_main:main` | Solo paso Cursor CLI (sin pipeline completo). |
| `paper-loop` | `paper_pipeline.integrated_loop_main:main` | Bucle reactivo: `@PERPLEXITY` / `@NOTION` / `@CURSOR`, meta-loop opcional, detección de stall opcional. |
| `paper-racing-loop` | `paper_pipeline.racing_loop_main:main` | Variante con carreras / límites (`RACING_LOOP_MAX`, etc.). |
| `paper-web` | `paper_pipeline.server_cli:main` | Servidor FastAPI + arranque asistido; Cockpit en `web/`. |
| `paper-parallel` | `paper_pipeline.parallel_cli:main` | Batch en worktrees; prefijos de comando en `PAPER_PIPELINE_PARALLEL_CMD_PREFIXES` o misión. |
| `paper-agent-step` | `paper_pipeline.agent.scheduler:main` | Un paso del scheduler en modo `autonomy` (dry-run por defecto). |
| `paper-report-figures` | `paper_pipeline.reporting.paper_figures:main` | Figuras / informes desde artefactos del paper. |
| `paper-agent-eval-check` | `paper_pipeline.agent_eval.check_cli:main` | Ejecuta `python -m paper_pipeline.agent_eval --check-baseline examples/baselines/agent_eval_baseline.json` (ruta por defecto; ejecutar desde la raíz del repo). |
| `paper-export-appendix` | `paper_pipeline.reporting.appendix_export:main` | Escribe `VERSION`, `git_commit.txt`, `agent_eval_report.json`, `pytest_collect.txt`, **`case_study_trace.json`** (sin secretos; `--repo-root` y `--case-study-outputs` opcionales). |

**Módulos auxiliares** (sin entrada en `project.scripts`; `python -m …`):

| Invocación | Rol breve |
|------------|-----------|
| `python -m paper_pipeline.reporting.benchmark_bundle -o archivo.json` | Escribe **`benchmark_bundle.json`**: `agent_eval` por escenario + `case_study_trace` + duraciones de fase del ledger (sin red). |
| `python scripts/audit_abstract_numbers.py` | Tabla Markdown en stdout: números del abstract vs `run_ledger` / `claims` / triaje (Plan v3); sin red. |

**No** se instala con `pip`: el binario **`agent`** de Cursor (ver [04-integraciones.md](04-integraciones.md)).

## Extras opcionales (`pip install -e ".[extra]"`)

| Extra | Uso |
|-------|-----|
| `dev` | pytest, ruff, httpx, pytest-asyncio. |
| `e2e` | Playwright (demo visual y Cockpit E2E). |
| `rag_qdrant` | Cliente Qdrant para RAG alternativo a Postgres. |
| `figures` | matplotlib para informes/figuras. |
| `experiments` | numpy para benchmark mínimo integrado. |
| `llm` | torch, transformers, datasets, accelerate para `experiment_runner.profile: hf_llm_micro`. |

## Variables de entorno: dónde está cada cosa

- **Guía por criterio (cuándo tocar qué):** [VARIABLES_Y_FLAGS.md](../VARIABLES_Y_FLAGS.md).
- **Lista comentada al estilo plantilla:** [`.env.example`](../../.env.example).
- **Tabla breve en el README raíz:** sección «Variables de entorno» del [README.md](../../README.md).

### Nombres usados en código y a veces omitidos en tablas cortas

| Variable | Dónde aplica | Notas |
|----------|--------------|-------|
| `LOOP_MIN_DELTA_CHARS` | `paper-loop` / stall | Cambio mínimo de caracteres en el borrador para no contar «sin progreso» (default 20). |
| `LOOP_STALL_MAX_CONSECUTIVE` | idem | Alias relacionado con `LOOP_STALL_CONSECUTIVE` (ver `.env.example`). |
| `RACING_LOOP_MAX` | `paper-racing-loop` | Máximo de ciclos (default 12). |
| `META_MAX_ROUNDS` | `paper-meta-loop`, tramo meta de `paper-loop` | Tope de rondas del revisor (default 12). |
| `META_WATCH_POLL`, `META_WATCH_DEBOUNCE`, `META_WATCH_EXIT_ON_STOP` | `paper-meta-watch` | Polling, debounce, salir si el hijo para. |
| `PAPER_EXPERIMENT_TIMEOUT_SEC` | `user_script_runner` | Override de timeout del script de experimento (además de `mission.experiment_runner.subprocess_timeout_sec`). |
| `PAPER_OUTPUT_DIR` | plantilla `run_experiment` | Directorio de salida esperado por scripts (default `outputs`). |
| `CURSOR_AGENT_VERSION_EXPECTED` | `cursor_cli_runner` (backend `cli`) | Si `agent --version` no contiene esta cadena, advertencia en `run.log`. |
| `CURSOR_AGENT_BACKEND` | `cursor_sdk_runner` / `cursor_cli_runner` | `sdk` (default) o `cli`. |
| `CURSOR_AGENT_MODEL` | `cursor_sdk_runner` | Modelo local SDK (default `composer-2.5`). |
| `CURSOR_AGENT_RESUME` | `cursor_sdk_runner` | Reanudar agente desde `cursor_agent_state.json` (default activo). |
| `PAPER_PIPELINE_TRIAGE_WEBHOOK_URL` | hipervisor | POST HTTPS opcional en tier 3 (ver `hypervisor/triage.py`). |

## Módulos de código clave (mapa rápido)

| Ruta | Contenido |
|------|-----------|
| `paper_pipeline/pipeline/runner.py` | Orquestador principal (`run_pipeline`). |
| `paper_pipeline/pipeline/experiment_phase.py` | Experiment runner integrado. |
| `paper_pipeline/pipeline/experiment_iteration.py` | Bucle post-Cursor + validación determinista. |
| `paper_pipeline/cursor_cli_runner.py` | Dispatcher SDK/CLI, prompts y reintentos. |
| `paper_pipeline/cursor_sdk_runner.py` | Backend Cursor SDK (`Agent.create` / `resume`). |
| `paper_pipeline/integrated_loop_main.py` | `paper-loop`. |
| `paper_pipeline/server/` | FastAPI, routers Cockpit, SSE. |
| `paper_pipeline/brain/` | Cerebro Gemini + prompts. |
| `paper_pipeline/hypervisor/` | Triaje, métricas. |
| `paper_pipeline/agent/` | Scheduler, goals, objetivo. |

## Ver también

- [02-orquestador.md](02-orquestador.md) — orden de fases.
- [03-servidor-api.md](03-servidor-api.md) — HTTP.
- [04-integraciones.md](04-integraciones.md) — Perplexity, Notion, Cursor, bucle experimento.
- [OUTPUTS_REFERENCE.md](../OUTPUTS_REFERENCE.md) — árbol de artefactos en `outputs/`.
