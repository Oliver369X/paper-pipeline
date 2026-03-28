# Variables de entorno y flags (0/1): guía y criterio

Este documento lista las variables que suelen interpretarse como **activado / desactivado** (`0`, `1`, `true`, `false`, a veces vacío = “usar default del código”) y explica **cuándo merece la pena tocarlas** y **qué ya hace el sistema sin que tengas que memorizar flags**.

## Por qué hay tantas opciones (y cómo no volverse loco)

- **Secretos y entorno** (API keys, rutas al `agent.exe`, base de datos) **tienen que vivir fuera del repo**: eso es `.env`.
- **Comportamiento por tarea** (¿esta misión necesita Cursor CLI?, ¿cuánta Perplexity?, ¿bloquear si el experimento falla?) debería vivir en **`mission.md`** cuando exista el campo equivalente: así cada paper define su propio “modo” sin que cambies el `.env` global cada vez.
- Los flags **globales en `.env`** sirven para: **override de emergencia**, **política del laboratorio** (p. ej. “en CI siempre estricto”) o **depuración** (apagar resume, logs, etc.).

**Orden práctico recomendado**

1. Ajustar **`mission.md`** (requisitos de la tarea).
2. Solo si no hay campo o necesitás política única para todo el servidor, usar **`.env`**.
3. Si algo puede **inferirse** (p. ej. prompt largo en Windows → stdin automático), **no hace falta flag** salvo override manual documentado abajo.

## Convención de valores

| Entrada típica | Significado |
|----------------|-------------|
| `1`, `true`, `yes` (sin importar mayúsculas) | Activado |
| `0`, `false`, `no` | Desactivado |
| Variable ausente o cadena vacía | **Default del código** (cada variable tiene su default; no asumas “0” universal) |

Algunas variables usan nombres **`DISABLE_*`**: un `1` **apaga** una función (sentido invertido respecto a “habilitar”).

---

## Cerebro (Gemini) y chat API

| Variable | Default típico | Qué hace |
|----------|----------------|----------|
| `BRAIN_USE_PERPLEXITY_CONTEXT` | desactivado si vacío | Antes del chat del cerebro, una pasada Perplexity (resumen web) si hay token. |
| `BRAIN_FORCE_PERPLEXITY_ON_ARXIV` | **1** | Si el último mensaje cita arXiv, fuerza contexto Perplexity aunque `BRAIN_USE_PERPLEXITY_CONTEXT` esté apagado. |
| `BRAIN_DEFAULT_RUN_PIPELINE_ON_APPLY` | **0** | Si en `POST .../brain/apply` omitís ejecutar pipeline, `1` dispara pipeline por defecto. |
| `BRAIN_MAX_RAG_CONTEXT_CHARS` | 4000; **0** desactiva solo el bloque RAG inyectado | Requiere RAG configurado (`BRAIN_RAG_ENABLED`). |

**Automático / por tarea:** el modelo y límites de historia suelen bastar con defaults; activá Perplexity en cerebro solo cuando el brief necesite web fresca o estéis iterando papers con muchas referencias.

---

## RAG (recuperación semántica)

| Variable | Default | Qué hace |
|----------|---------|----------|
| `BRAIN_RAG_ENABLED` | desactivado si vacío | Inyecta RAG en el cerebro e indexa tras pipeline/apply. |
| `RAG_EMBEDDING_USE_VERTEX` | desactivado si vacío | `1` → Vertex AI; si no, API key tipo Gemini embeddings. |

**Por tarea:** activar RAG solo en misiones con corpus grande o cuando el chat necesite memoria semántica del repo; no hace falta encenderlo para cada paper corto.

---

## Perplexity (pipeline, meta-loop, cerebro)

| Variable | Notas |
|----------|--------|
| `PERPLEXITY_SESSION_TOKEN` | Cookie/sesión; no es 0/1 pero es el prerequisito de casi todo lo “web”. |

**Por tasa de llamadas:** muchos pasos `perplexity:*` están gobernados por **`mission.md`** (`max_perplexity_calls`, secciones, resume). Preferí eso antes que flags globales.

---

## Cursor CLI (agent headless)

| Variable | Default / notas | Qué hace |
|----------|-----------------|----------|
| `CURSOR_CLI_PROMPT_STDIN` | automático en Windows si el prompt supera umbral | `1` fuerza enviar prompt por stdin; `0` fuerza argv (riesgo de línea demasiado larga en Windows). |
| `PAPER_PIPELINE_CURSOR_CLI_OPTIONAL` | alineado con `mission.cursor_cli_optional` | `1` = un fallo del agente **no** aborta el run (override de política vía env). |
| `CURSOR_CLI_MAX_ROUNDS` | (opcional) | Si está definido, fija el **máximo de invocaciones** del `agent` por run (1–20); pisa `debugging.cursor_max_attempts` en `mission.md`. |

**Reintentos con contexto:** si un intento termina con error, el siguiente prompt incluye la salida (stdout/stderr) del intento anterior para que el agente codificador pueda corregir o iterar. El **primer exit 0** corta el bucle. El tope por misión es **`debugging.cursor_max_attempts`** (default 3; poné `1` para un solo disparo como antes). Resumen en `outputs/cursor_cli_rounds.json`.

**Bucle experimento post-Cursor (opcional):** con `enable_experiment_runner`, `code_needed`, `enable_cursor_cli` y `experiment_runner.iteration_after_cursor: true`, el experimento integrado **no** corre antes del quality check; después del primer `cursor_cli` exitoso corre un bucle (hasta `experiment_runner.iteration_max_rounds`): ejecutar script → validación determinista de `metrics.json` (`outputs/validation/experiment_deterministic.json`) → `experiment_iteration_hint.md` → opcional `iteration_perplexity_on_fail` → otro `cursor_cli` si aún hay rondas. Cotas opcionales: `experiment_runner.deterministic_metrics_bounds`.

**Automático:** en Windows, prompts largos pasan a stdin solos (umbral `CURSOR_CLI_WIN_MAX_ARG_CHARS`, default 6000). La decisión “¿esta misión necesita Cursor?” es **`enable_cursor_cli` + `cursor_cli_optional` en `mission.md`**.

---

## Pipeline: experimentos, honestidad y reanudación

| Variable | Sentido | Qué hace |
|----------|---------|----------|
| `PAPER_PIPELINE_STRICT_EXPERIMENT` | activado = más estricto | Fuerza fallo de run si `metrics.json` indica error del experiment runner (override de política). |
| `PAPER_PIPELINE_INVALIDATE_PERPLEXITY_ON_EXP_FAIL` | activado | Tras fallo crítico, también invalida pasos `perplexity:*` en el estado (regenera secciones; más cuota Perplexity). |
| `PAPER_PIPELINE_DISABLE_RESUME` | **1 = apaga** resume | No reutiliza `run_state` como venías haciendo. |
| `PAPER_PIPELINE_DISABLE_RUN_LOG` | **1 = apaga** `run.log` JSONL | Menos trazabilidad; solo para depuración o entornos ruidosos. |
| `PAPER_PIPELINE_DISABLE_EVENTS` | **1 = apaga** emisión de eventos | Uso avanzado (SSE/web). |

**Por tarea:** `block_pipeline_on_failure`, perfiles de `experiment_runner`, etc. van en **`mission.md`**. El `.env` aquí es para **laboratorio/CI** o “modo seguro global”.

---

## Loops, publicación y meta-herramientas

| Variable | Qué hace |
|----------|----------|
| `LOOP_STALL_DETECT` | Detectar estancamiento del loop integrado (`1`/`true`/`yes`). |
| `LOOP_STALL_CONSECUTIVE` / `LOOP_STALL_MAX_CONSECUTIVE` | Ciclos seguidos sin cambio de borrador antes de considerar stall (default 2). |
| `LOOP_MIN_DELTA_CHARS` | Cambio mínimo de caracteres en el borrador para contar progreso (default 20). |
| `RACING_LOOP_MAX` | Tope de ciclos en `paper-racing-loop` (default 12). |
| `META_MAX_ROUNDS` | Tope de rondas del revisor en `paper-meta-loop` / tramo meta de `paper-loop` (default 12). |
| `META_WATCH_POLL`, `META_WATCH_DEBOUNCE`, `META_WATCH_EXIT_ON_STOP` | `paper-meta-watch`: intervalo de polling, debounce al guardar, salir si el proceso hijo para. |
| `PAPER_PIPELINE_BUILD_PACKS` | Generar packs al publicar (cuando aplique elegibilidad + condiciones). |
| `PAPER_PIPELINE_PERPLEXITY_STRATEGY` | Registrar perfiles en `perplexity_call_record.jsonl`. |
| `PAPER_PIPELINE_AUTONOMY_EXECUTE` | Permite que decisiones de autonomía marquen ejecución real cuando el cableado exista (`would_execute`). |
| `PAPER_PIPELINE_RELAX_METRICS` | Hipervisor: relajar parseo de métricas cuando el bundle falla parcialmente. |
| `PAPER_PIPELINE_TRIAGE_WEBHOOK_URL` | Webhook HTTPS opcional en triaje tier 3 (breakthrough). |

## Experimentos (scripts bajo `outputs/code/`)

| Variable | Qué hace |
|----------|----------|
| `PAPER_EXPERIMENT_TIMEOUT_SEC` | Override del timeout del subprocess de `run_experiment.py` (además de `experiment_runner.subprocess_timeout_sec` en la misión). |
| `PAPER_OUTPUT_DIR` | Directorio de salida que esperan plantillas/scripts (default `outputs`). |

## Cursor CLI (complemento)

| Variable | Qué hace |
|----------|----------|
| `CURSOR_AGENT_VERSION_EXPECTED` | Si `agent --version` no contiene esta cadena, advertencia en `run.log` (compatibilidad de entorno). |

---

## Observabilidad y rutas

| Variable | Notas |
|----------|--------|
| `PAPER_PIPELINE_DATA_DIR` | Carpeta de misiones para la API web (default relativo al cwd del servidor). |
| `PAPER_PIPELINE_PARALLEL_CMD_PREFIXES` | Lista de prefijos permitidos para comandos en flujos paralelos. |
| `PAPER_PIPELINE_CORS_ORIGINS` | Lista separada por comas de orígenes extra para CORS (p. ej. `https://tu-app.vercel.app` cuando el SPA está en Vercel y el API en otro host). Los orígenes de desarrollo (Vite) se añaden siempre. |

## Frontend (Vite / Vercel)

| Variable | Dónde | Qué hace |
|----------|--------|----------|
| `VITE_API_BASE_URL` | **Build** del SPA (`web/`) | URL absoluta del API si el HTML se sirve desde otro dominio (Vercel) y el FastAPI está en otro host. Sin definir: rutas relativas `/api/...` (mismo origen o proxy en dev). Ver `web/README.md`. |

---

## Cómo elegir sin memorizar decenas de flags

1. **Definí la tarea en `mission.md`** (secciones, límites, experiment runner, Cursor opcional, quality check).
2. **Dejá `.env` para credenciales y defaults estables** del entorno (keys, `DATABASE_URL`, `CURSOR_AGENT_BIN` en Windows).
3. Usá flags **0/1 globales** solo cuando necesites **misma política para todas las misiones** (estricto en CI, invalidar Perplexity siempre tras fallo de experimento, etc.).
4. Si un comportamiento es **condicional al contexto** (longitud del prompt, OS, fallo reciente), **preferí lógica automática en código**; este repo ya aplica varios casos (stdin en Windows, fallbacks documentados en `.env.example`).

Para capas de evaluación rigurosa vs asistida, seguí también `docs/technical/EVALUATION_LAYERS.md`.

Huellas empíricas, invalidación de resume y `pipeline_provenance.json`: `docs/technical/EMPIRICAL_DEPENDENCIES.md`. En `mission.md`, `quality_gates.epistemic_alignment_mode` y `downstream_metrics_mode` (`off` / `warn` / `block`) controlan gates sobre réplica vs tier degradado.

**Inventario complementario** (comandos `paper-*`, extras pip, nombres de env dispersos): [technical/07-inventario-cli-y-entorno.md](technical/07-inventario-cli-y-entorno.md).
