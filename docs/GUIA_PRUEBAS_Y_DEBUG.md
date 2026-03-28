# Guía de pruebas y depuración (CLI, API y flujos completos)

Este documento está pensado para **validar cada pieza por separado** (sin depender solo de la interfaz web) y luego **encadenar flujos de punta a punta**. La web es una capa encima: si algo falla, conviene aislar si el problema está en el **pipeline Python**, en el **servidor HTTP**, o en el **frontend**.

---

**Comando de tests por defecto (sin Perplexity/Notion “real”, sin E2E navegador):** `pytest -m "not integration and not notion_real and not e2e and not cockpit_e2e and not autonomy_integration" -q` (ver `pyproject.toml` y [README.md](README.md) en esta carpeta).

**Escenarios manuales E2E (operador, M1–M6):** [E2E_SCENARIOS.md](E2E_SCENARIOS.md) — matriz con pasos, comandos opcionales (`integration`, `autonomy_integration`, `cockpit_e2e`) y líneas de investigación sugeridas.

### Fallos conocidos (integración en vivo, no bugs del repo)

Las pruebas que llaman a **Perplexity** o a la **red** pueden fallar **de forma intermitente** aunque el token sea válido:

| Síntoma | Causa probable | Qué hacer |
|---------|----------------|-----------|
| `ResponseParsingError` / `Query processing failed` | API o SSE de Perplexity inestable | Re-ejecutar solo ese test o el comando `paper-pipeline` |
| `curl: (56) Recv failure: Connection was reset` | Red intermitente (TLS/HTTP2) | Reintentar; no indica credencial incorrecta |
| `test_cursor_cli_integration` falla en Windows con `FileNotFoundError` al lanzar `agent` | `agent` suele ser **`agent.cmd`**; `subprocess` con lista de argv no ejecuta `.cmd` igual que en Unix | El test usa `shell=True` para `.cmd`/`.bat`; o definí `CURSOR_AGENT_BIN` con ruta absoluta al `.cmd` |

Para **aislar** fallos de red al correr la suite completa: `pytest -m "not integration and not notion_real and not autonomy_integration" -q`.

## 1. Filosofía rápida

| Capa | Qué te da | Límite |
|------|-----------|--------|
| **CLI** (`paper-pipeline`, `paper-loop`, …) | Salida en terminal, códigos de salida, logs `logging` | No hay SSE ni formularios |
| **`outputs/` + `run.log` (JSONL)** | Historial estructurado de pasos | Hay que abrir archivos o usar `jq` / editor |
| **API FastAPI** (`/api/...`) | Misma lógica que la web, probabile con `curl` o tests | Requiere servidor en marcha |
| **Web (Vite)** | UX; EventSource para SSE | Si la API cae, la UI solo muestra error genérico |

**Regla práctica:** para “¿funciona Perplexity / la misión / el loop?” → **CLI o tests**. Para “¿el servidor reenvía eventos?” → **API + `curl` o `test_server.py`**. Para “¿el usuario entiende el flujo?” → **web**.

---

## 2. Prerrequisitos comunes

### 2.1 Entorno Python

- Python **3.10+**
- Paquete **perplexity-webui-scraper** instalado en editable **antes** que `paper-pipeline` (ruta según tu árbol de carpetas; ver [README principal](../README.md#instalación)).
- En la carpeta `paper-pipeline`:

  ```bash
  pip install -e .
  pip install -e ".[dev]"   # pytest, httpx, ruff, etc.
  ```

### 2.2 Variables de entorno (mínimo)

| Variable | Obligatoria para | Notas |
|----------|------------------|--------|
| `PERPLEXITY_SESSION_TOKEN` | Cualquier llamada **real** a Perplexity | Cookie de sesión; no commitear. Suele ir en `.env` en la raíz de `paper-pipeline`. |
| `NOTION_TOKEN` | Sync Notion | Solo si `enable_notion: true` y `notion_page_id` en la misión. |
| `CURSOR_API_KEY` | Cursor CLI headless | Solo si usás `paper-cursor-agent` y bloques `@CURSOR` con agente real. |
| `PAPER_PIPELINE_DATA_DIR` | Solo **interfaz web** | Si no está, el servidor usa `./data/missions` relativo al cwd de uvicorn. |
| `PAPER_PIPELINE_RELAX_METRICS` | Triaje con JSON legacy | `1`/`true`: si falla `MetricsBundle` pero parsea como `TriageMetrics`, el triaje sigue (ver HIPERVISOR). |
| `LOOP_STALL_DETECT`, `LOOP_STALL_MAX_CONSECUTIVE`, `LOOP_MIN_DELTA_CHARS` | **`paper-loop`** | Detección de estancamiento del borrador y `outputs/loop/stop_decision.json`. |
| `PAPER_PIPELINE_BUILD_PACKS` | Publicación | `1` para generar `research_pack/` y `code_pack/` al escribir `publish_decision` si hay elegibilidad. |
| `PAPER_PIPELINE_PERPLEXITY_STRATEGY` | Pipeline Perplexity | `1`/`true`: append a `outputs/perplexity_call_record.jsonl` por sección (perfil/modo/hash); sin efecto en la respuesta del modelo. |

Los comandos `paper-*` cargan `.env` automáticamente vía `load_dotenv_if_available()` donde corresponda.

### 2.3 Archivo de misión (`mission.md`)

- Formato: **YAML frontmatter** entre `---` + cuerpo opcional.
- La clave de secciones es **`sections_needed`** (lista de strings), no `sections`.
- `output_dir` suele ser `outputs` (relativo al directorio de la misión o absoluto).

Ejemplo mínimo válido:

```yaml
---
topic: "Mi tema"
paper_target: "conferencia"
sections_needed:
  - gaps
  - methodology
max_perplexity_calls: 8
code_needed: false
enable_notion: false
enable_quality_check: true
enable_cursor_cli: false
model: best
language: en-US
output_dir: outputs
---
```

---

## 3. Códigos de salida (`ExitCode`)

Definidos en `paper_pipeline/constants.py`. Los más usados:

| Código | Significado (resumen) |
|--------|------------------------|
| `0` | OK (`paper-pipeline`, y en `paper-loop` “éxito normal” según último ciclo) |
| `1` | Error genérico |
| `2` | Misión no encontrada |
| `3`–`7` | Auth / rate limit / Cursor / Notion (según contexto) |
| `8` | `LOOP_STALLED` — borrador sin cambiar entre ciclos (detección opcional en `paper-loop`) |

**Nota:** `run_meta_loop` usa internamente **0 = CONTINUE, 1 = STOP**, distinto del uso global de `ExitCode.ERROR = 1`. `paper-loop` trata `last in (0, 1, 2)` como fin de ciclo normal en muchos casos; detalle en [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md).

---

## 4. Probar cada pieza por separado

### 4.1 `paper-pipeline` / `python -m paper_pipeline`

**Qué hace:** Orquesta Perplexity por secciones, ensambla `draft_paper.md`, quality check opcional, Notion opcional.

| Entrada | Descripción |
|---------|-------------|
| `mission.md` (o ruta) | Archivo de misión |
| `--dry-run` | Sin llamadas a Perplexity; valida misión y escribe en `run.log` de forma acotada |

**Salida esperada:**

- `0` si todo OK (dry-run o real).
- `2` si el archivo de misión no existe.
- En `outputs/` (según `output_dir`): `run.log`, `run_state.json`, secciones `.md`, etc. Ver [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md).

**Cómo probar sin red (solo validación):**

```bash
cd paper-pipeline
paper-pipeline mission.md --dry-run
echo ExitCode: %ERRORLEVEL%   # Windows
# echo $?                     # Linux/macOS
```

**Cómo probar con Perplexity real:**

- `.env` con `PERPLEXITY_SESSION_TOKEN`.
- Sin `--dry-run`.

**Depuración:**

- Consola: mensajes `logging` del orquestador.
- `outputs/run.log`: líneas JSON (`step_start`, `step_ok`, `step_error`, …).
- Si `draft_paper.md` no aparece en dry-run: **es esperado** (dry-run no genera el borrador completo como ejecución real).

---

### 4.2 `paper-loop` (`paper_pipeline.integrated_loop_main`)

**Qué hace:** Lee directivas en `outputs/cursor_turn.md` y `outputs/next_instruction.md`, ejecuta `@PERPLEXITY` / `@NOTION` / `@CURSOR`, puede ejecutar meta-loop.

| Entrada | Descripción |
|---------|-------------|
| `mission.md` | Ruta a la misión |
| `--output-dir` | Override del directorio de salida (default: `mission.output_dir`) |
| `--max-cycles N` | Repetir ciclos |
| `--no-meta` | Sin meta-loop |
| `--dry-run` | Lista directivas sin APIs |
| Env `LOOP_STALL_DETECT=1` | Detección de borrador sin cambios entre ciclos (ver `LOOP_STALL_CONSECUTIVE`) |

**Salida esperada:**

- Proceso termina con `0` si el último ciclo está en “rango aceptado” (ver código en `integrated_loop_main.py`).
- `8` si `draft_unchanged_between_cycles` y detección activa.

**Cómo probar sin red:**

```bash
paper-loop mission.md --dry-run --max-cycles 1
```

**Depuración:**

- `outputs/run.log`
- `outputs/cursor_turn.md` — debe ser UTF-8; el bucle **stripa** bloques ejecutados.

---

### 4.3 `paper-meta-loop`

**Qué hace:** Una vuelta del meta-agente (revisor sobre `outputs/`).

**Probar:** `paper-meta-loop --output-dir outputs` (desde directorio donde exista `outputs/` coherente con una misión ya corrida).

**Salida:** Hoy el CLI puede hacer `sys.exit(0)` siempre en algunos caminos; revisar `meta_main.py` si necesitás códigos exactos.

---

### 4.4 `paper-meta-watch`

**Qué hace:** Observa cambios (polling + debounce) y reacciona a `cursor_turn.md`.

**Variables útiles:** `META_WATCH_POLL`, `META_WATCH_DEBOUNCE` (ver código / README).

---

### 4.5 `paper-cursor-agent`

**Qué hace:** Invoca el binario Cursor `agent` en modo headless.

| Entrada | Descripción |
|---------|-------------|
| `CURSOR_API_KEY` | En `.env` |
| `--dry-run` | Sin ejecutar agente real |

**Depuración:** `outputs/cursor_cli.log`; `where agent` (Windows) o `which agent` (Unix) para saber qué binario se usa.

---

### 4.6 Interfaz web — API (sin navegador)

Con el servidor en `127.0.0.1:8000` y `PAPER_PIPELINE_DATA_DIR` apuntando a una carpeta de prueba si querés aislar datos:

| Método | Ruta | Uso |
|--------|------|-----|
| `GET` | `/api/health` | Comprobar que uvicorn responde |
| `GET` | `/api/models` | Lista de modelos Perplexity |
| `GET` | `/api/missions` | Lista misiones |
| `POST` | `/api/missions` | Crear misión (JSON `MissionCreate`) |
| `GET` | `/api/missions/{id}` | Detalle + `meta` + `mission` |
| `PATCH` | `/api/missions/{id}` | Actualizar |
| `POST` | `/api/missions/{id}/run?dry_run=true` | Ejecutar pipeline en thread (sin Perplexity si `dry_run=true`) |
| `GET` | `/api/missions/{id}/events/{run_id}` | **SSE** (stream de eventos) |
| `GET`/`PUT` | `/api/missions/{id}/draft` | Borrador |
| `POST` | `/api/missions/{id}/loop` | Escribe `cursor_turn.md` + `run_integrated_cycle` |
| `GET` | `/api/missions/{id}/ledger/latest` | `run_ledger.json` |
| `GET` | `/api/missions/{id}/evidence/latest` | `evidence_index.json` |
| `GET` | `/api/missions/{id}/triage/latest` | `triage_report.json` |
| `GET` | `/api/missions/{id}/publish/decision` | `publish_decision.json` completo |
| `POST` | `/api/missions/{id}/publish/preview` | `{ eligible, blocking_reasons }` (sin 404 si falta archivo) |
| `GET` | `/api/missions/{id}/loop/stop` | `stop_decision.json` (404 si no hubo parada por stall) |
| `GET` | `/api/missions/{id}/metrics/validated` | `{ ok, errors }` — validación estricta `MetricsBundle` |
| `GET` | `/api/missions/{id}/safety/latest` | Última decisión de `safety_trace.jsonl` |
| `GET` | `/api/missions/{id}/objective/latest` | Estado consolidado de `objective_state.json` |
| `GET` | `/api/missions/{id}/memory/latest` | Último evento de `research_memory.jsonl` |
| `GET` | `/api/missions/{id}/memory/index` | Índice barato de `memory_index.json` |
| `GET` | `/api/missions/{id}/goal-selection/latest` | Recomendación actual de `goal_selection.json` |

**Ejemplo `curl` (PowerShell puede requerir comillas distintas):**

```bash
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/missions
```

**Salida esperada:** JSON; `POST .../run` devuelve `{"run_id":"..."}` para abrir el SSE.

**Safety V1:** si el sistema escribió `outputs/safety_trace.jsonl`, podés inspeccionar la última decisión por API con `GET /api/missions/{id}/safety/latest`. Esa línea resume `candidate_action`, `decision`, `rule_id`, `reasons` y `source_artifacts`.

**Objective State V1:** si el sistema escribió `outputs/objective_state.json`, podés inspeccionar el estado consolidado con `GET /api/missions/{id}/objective/latest`. Resume utilidad total, términos y gates a partir de quality, triage, publish, ledger, loop y safety.

**ResearchMemory V1:** si el sistema escribió `outputs/research_memory.jsonl` y `outputs/memory_index.json`, podés inspeccionar el último evento y el índice barato con `GET /api/missions/{id}/memory/latest` y `GET /api/missions/{id}/memory/index`.

**Goal Selection V1:** si el sistema escribió `outputs/goal_selection.json`, podés inspeccionar la recomendación actual con `GET /api/missions/{id}/goal-selection/latest`. El loop API también puede reutilizar esa selección como `goal` si no se pasa uno explícito.

---

## 5. Tests automatizados

**Suite habitual (sin integración Perplexity real):**

```bash
cd paper-pipeline
pytest tests/ -q --ignore=tests/test_perplexity_integration.py
```

**Marcadores:**

| Marcador | Significado |
|----------|-------------|
| `integration` | `test_perplexity_integration.py` — llamada real; consume cuota; requiere token |
| `e2e` | Playwright / visual-flow; requiere `pip install -e ".[e2e]"` y `playwright install chromium` |

**Servidor web:**

```bash
pytest tests/test_server.py -q
```

**SafetyController V1:**

```bash
pytest tests/test_safety_controller.py -q
```

**Objective State V1:**

```bash
pytest tests/test_objective_state.py -q
```

**ResearchMemory V1:**

```bash
pytest tests/test_research_memory.py -q
```

**Goal Selection V1:**

```bash
pytest tests/test_goal_selection.py -q
```

**Agent eval harness (oráculos deterministas, sin Perplexity):** valida `SafetyController` y `GoalSelector` contra escenarios JSON versionados en `paper_pipeline/agent_eval/eval_scenarios/`. Ver [technical/agent-eval-spec.md](technical/agent-eval-spec.md).

```bash
pytest tests/test_agent_eval_runner.py -q
python -m paper_pipeline.agent_eval --out /tmp/eval_report.json
```

**Goal Manager + memoria V2 (thin):**

```bash
pytest tests/test_goals_manager.py tests/test_strategic_memory.py -q
```

**Cobertura (opcional):**

```bash
pytest tests/ --cov=paper_pipeline --cov-report=term-missing --ignore=tests/test_perplexity_integration.py
```

---

## 6. Flujos “de punta a punta” (checklist manual)

### 6.1 Solo pipeline (CLI)

1. Crear `mission.md` válido en una carpeta de prueba.
2. `paper-pipeline mission.md --dry-run` → código `0`, revisar `outputs/run.log`.
3. Con token: `paper-pipeline mission.md` → revisar `outputs/*.md`, `draft_paper.md`, `run_state.json`.

### 6.2 Loop + directivas

1. Tener `outputs/cursor_turn.md` con bloques `@PERPLEXITY:...` o `@CURSOR` según [docs/cursor_turn.example.md](cursor_turn.example.md) y [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md).
2. `paper-loop mission.md --max-cycles 1 --dry-run` → ver qué haría.
3. Sin `--dry-run` → revisar `run.log`, `draft_paper.md`, `next_instruction.md`.

### 6.3 Web (MVP)

1. Terminal A: `paper-web --reload` (desde `paper-pipeline` con venv).
2. Terminal B: `cd web && npm run dev` **o** `npm run dev:all` (solo `web/`).
3. Abrir navegador en la URL de Vite (p. ej. `http://localhost:5173`).
4. Crear misión → Editor → Guardar → Pipeline (sin dry-run solo si hay token) → Borrador → Loop → Logs.
5. Si la lista de misiones falla: leer el mensaje en Home (ayuda a API caída) y comprobar `GET /api/health` con `curl`.

---

## 7. Dónde mirar cuando algo falla

| Síntoma | Dónde mirar primero |
|---------|---------------------|
| El pipeline corre pero **no ves el hilo** en perplexity.ai | Misma cuenta que la cookie del token; pestaña **Biblioteca / Library** y actividad reciente. En consola, tras cada `ask` OK, el CLI registra `Perplexity thread backend_uuid=…`: confirma que la llamada es real. La UI no siempre lista al instante hilos creados vía API interna; plan de cuenta, “memoria” o privacidad pueden afectar. |
| “No se conecta a la API” en la web | ¿Corre uvicorn en 8000? ¿`npm run dev` con proxy? Firewall local. |
| `401` / auth Perplexity | Token caducado o inválido; renovar cookie en Perplexity. |
| Sección no generada | `run.log` → `step_error` o `step_skip`; `max_perplexity_calls`; `run_state.json` por reanudación. |
| Cursor no encuentra agente | `where agent` / `which agent`; `CURSOR_AGENT_BIN` si aplica. |
| Loop no cambia el borrador | `LOOP_STALL_DETECT`; contenido de `cursor_turn.md`; `draft_unchanged_between_cycles` en log. |

**Herramientas:**

- **JSONL:** abrir `outputs/run.log` en editor o filtrar líneas con `step_error`.
- **Windows:** `where python`, `where agent`, `echo %ERRORLEVEL%` tras comandos.
- **Tests:** reproducir con el test más pequeño que toque el módulo (`pytest tests/test_loop_directives.py -q`, etc.).

---

## 8. Resumen de comandos útiles

```bash
# Validación rápida sin Perplexity
paper-pipeline mission.md --dry-run

# Loop en seco
paper-loop mission.md --dry-run --max-cycles 1

# Tests Python (sin integración Perplexity)
pytest tests/ -q --ignore=tests/test_perplexity_integration.py

# API servidor
paper-web --reload
curl -s http://127.0.0.1:8000/api/health

# Frontend
cd web && npm run dev
# o
cd web && npm run dev:all
```

---

## 9. Documentos relacionados

- [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md) — flujo conceptual y bucles.
- [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md) — qué archivo significa qué.
- [ESTADO_Y_OBJETIVO.md](ESTADO_Y_OBJETIVO.md) — alcance del proyecto.
- [README principal](../README.md) — instalación e interfaz web.

---

*Última actualización: orientada a depuración por componentes y pruebas reproducibles sin depender solo de la UI.*
