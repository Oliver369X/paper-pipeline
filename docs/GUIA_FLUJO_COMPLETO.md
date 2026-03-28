# Guía: qué hace cada comando, bucles, “volver atrás” y Cursor CLI

Documento orientado a uso práctico. Las claves van en `.env` (ver [`.env.example`](../.env.example)); el venv solo aísla **Python**, no sustituye `.env`.

---

## 1. Piezas principales (qué es cada una)

| Herramienta | Rol |
|-------------|-----|
| **`paper-pipeline`** (`mission.md`) | Flujo **lineal**: Perplexity por secciones → `draft_paper.md` → **experiment_runner** (si `enable_experiment_runner`) → calidad opcional → Notion opcional → Cursor CLI opcional si `enable_cursor_cli` + `code_needed`. Si `experiment_runner.iteration_after_cursor: true`, el experimento con script puede ejecutarse **después** de Cursor (bucle con validación determinista de métricas). |
| **`paper-loop`** | Flujo **reactivo**: lee directivas `@PERPLEXITY` / `@NOTION` / `@CURSOR` en `outputs/cursor_turn.md` y `outputs/next_instruction.md`, ejecuta APIs, actualiza borrador si hubo secciones nuevas, luego **meta-loop** (Perplexity revisor). |
| **`paper-meta-loop`** | **Una** ronda: lee `cursor_turn.md` → llama a Perplexity → escribe `next_instruction.md` (CONTINUE o STOP). |
| **`paper-meta-watch`** | Igual que meta-loop pero **cada vez que guardás** `cursor_turn.md` (con debounce). |
| **`paper-cursor-agent`** | Solo el paso Cursor CLI (sin orquestar todo el paper). |
| **`visual-flow/index.html`** | **Demo visual** sin APIs; no sustituye los comandos anteriores. |

---

## 2. Flujo lineal típico (`paper-pipeline`)

1. **Leés/editás** `mission.md` (tema, secciones, `max_perplexity_calls`, flags).
2. **Ejecutás** `paper-pipeline mission.md` (con `PERPLEXITY_SESSION_TOKEN` en `.env`).
3. **Ocurre** (en orden interno; ver [technical/02-orquestador.md](technical/02-orquestador.md)):
   - Por cada sección permitida: una conversación Perplexity → `outputs/<sección>.md`.
   - Si `code_needed`: `outputs/code/README.md`.
   - Se arma `draft_paper.md`.
   - Si `enable_experiment_runner` **y no** está activo `experiment_runner.iteration_after_cursor` (con `code_needed` + `enable_cursor_cli`): se ejecuta el experimento integrado y se escribe `metrics.json` **antes** del quality check.
   - Si `enable_quality_check` y hay cupo: `quality_gaps.md`.
   - Notion si está activado y hay `NOTION_TOKEN`.
   - Si `enable_cursor_cli` y `code_needed`: se llama al binario **`agent`** (Cursor CLI headless) **hasta** `debugging.cursor_max_attempts` veces si falla (reintentos con contexto): `outputs/cursor_cli_rounds.json`.
   - Si `iteration_after_cursor` está activo: **después** del primer `cursor_cli` exitoso corre el bucle experimento → validación determinista → pistas → más `cursor_cli` si aplica (ver [VARIABLES_Y_FLAGS.md](VARIABLES_Y_FLAGS.md)).
4. **Salida:** carpeta `outputs/` con los archivos anteriores ([OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md)).

**¿Se puede “volver atrás” un paso dentro del script?** No hay deshacer automático. Si algo salió mal, usás **git** (`git checkout outputs/`) o restaurás backups. El pipeline **no** implementa rollback.

---

## 3. Flujo reactivo / bucle (`paper-loop`)

1. En `outputs/cursor_turn.md` o `outputs/next_instruction.md` escribís bloques como:
   - `@PERPLEXITY:gaps` + texto opcional debajo.
   - `@NOTION` (una línea).
   - `@CURSOR` + texto opcional (prompt extra para el agente).
2. **Ejecutás** `paper-loop mission.md` (y opcionalmente `--output-dir`, `--max-cycles N`, `--no-meta`, `--dry-run`).
3. **Por ciclo:**
   - Se ejecutan las directivas **en orden** (primero lo que haya en `cursor_turn.md`, luego `next_instruction.md`).
   - Tras ejecutar, esos bloques se **eliminan** del markdown (para no repetirlos).
   - Si hubo `@PERPLEXITY`, se **regenera** `draft_paper.md`.
   - Si no usás `--no-meta`, corre **`paper-meta-loop`**: lee `cursor_turn.md` y escribe un `next_instruction.md` nuevo (CONTINUE/STOP).
4. **`--max-cycles`:** repite ese ciclo hasta **STOP** del meta-loop (código de salida 1) o hasta agotar N ciclos.

**¿Es un loop infinito?** No por defecto: `max-cycles` limita repeticiones; el meta-loop también puede decir **STOP** y el límite `META_MAX_ROUNDS` aplica al revisor.

**¿Puede “saltar” a otra parte del flujo (p. ej. solo Notion sin Perplexity)?** Sí **metiendo solo las directivas que quieras** en ese momento. No hay un “paso 3 del asistente” fijo: el orden lo marcan **tus** `@…` y el contenido de `cursor_turn` / `next_instruction`.

**¿Puede volver “al principio” del pipeline lineal?** Volviendo a ejecutar `paper-pipeline` (sobrescribe secciones según misión). No hay máquina de estados con “ir al paso 2” salvo que **vos** edites archivos y directivas.

---

## 4. Integración (qué tan “cerrado” está el sistema)

| Integración | Estado |
|-------------|--------|
| Perplexity (Python + sesión) | Integrado en orquestador, meta-loop, `paper-loop` con `@PERPLEXITY`. |
| Notion | Integrado en orquestador y `@NOTION` en `paper-loop`. |
| Cursor CLI | Integrado vía `subprocess` al binario **`agent`** en PATH; requiere **`CURSOR_API_KEY`** y **instalación aparte** del CLI (no viene con `pip install paper-pipeline`). |
| IDE Cursor (chat manual) | No lo controla el script; usás `.cursorrules` y archivos en `outputs/`. |
| Demo `visual-flow` | No llama APIs; es ilustración. |

**Modelo Perplexity** en el pipeline: el de **`mission.md`** → campo `model` (p. ej. `best`).

**Modelo Cursor / agente:** el comando base es:

`agent -p --force --output-format text [argumentos extra] "<prompt>"`

Opcionalmente podés inyectar flags **antes** del prompt con **`CURSOR_AGENT_EXTRA_ARGS`** (una cadena con espacios; se parsea con `shlex`, podés usar comillas). Ejemplo (sintaxis exacta según la doc actual de Cursor):

`CURSOR_AGENT_EXTRA_ARGS=--model gpt-5`

Si no definís esa variable, el modelo lo elige **la herramienta Cursor CLI** (config por defecto). Revisá la [documentación oficial del CLI](https://cursor.com/docs/cli/headless) para los flags válidos.

**Dónde se ejecuta `agent`:**

- **Directorio de trabajo (`cwd`):** carpeta de la misión (padre de `mission.md`) o `cursor_cli_cwd` en la misión.
- **Proceso:** el mismo terminal / máquina donde corrés `paper-pipeline` o `paper-loop`; no se instala `agent` dentro del venv.

**¿La CLI ya está instalada al hacer `pip install`?** **No.** Tenés que instalarla según Cursor (p. ej. PowerShell: `irm 'https://cursor.com/install?win32=true' | iex` o lo que indique la doc actual) y comprobar que `agent` aparece en el PATH (`where agent` en Windows).

---

## 5. Cómo iterar (práctica)

1. **Iteración de investigación:** editás `mission.md` o añadís `@PERPLEXITY:sección` en `cursor_turn` / `next_instruction` y corrés `paper-loop`.
2. **Iteración código:** Cursor en el IDE **o** `@CURSOR` / `paper-cursor-agent` / `enable_cursor_cli` en el pipeline inicial.
3. **Iteración revisión:** `paper-meta-loop` o `paper-meta-watch` después de actualizar `cursor_turn.md`.

---

## 5.1 Modo autonomía (un paso sin red por defecto)

- En `mission.md`: `mode: autonomy` y opcional bloque `autonomy:` (límites; ver `paper_pipeline/mission.py`).
- **CLI:** `paper-agent-step --output-dir data/missions/<id>/outputs` (dry-run por defecto; `--no-dry-run` para el camino “real” sujeto a gates y `PAPER_PIPELINE_AUTONOMY_EXECUTE`).
- **API:** `POST /api/missions/{id}/agent/run-step` con `{"dry_run": true}` — escribe una línea en `outputs/agent_decisions.jsonl` (selección de meta, safety, política pre/post). No llama a Perplexity ni ejecuta el pipeline salvo que en el futuro se cablee esa invocación.
- Cockpit muestra la última decisión y (si existe) la última entrada de `perplexity_call_record.jsonl`.

## 5.2 Research pack (zip para revisión)

Con publicación elegible y `PAPER_PIPELINE_BUILD_PACKS=1`, el pipeline genera `outputs/research_pack/`. Para empaquetar:

```bash
cd outputs && zip -r ../research_pack.zip research_pack/
```

En Windows PowerShell podés usar **Comprimir** sobre la carpeta o `Compress-Archive -Path research_pack -DestinationPath research_pack.zip`.

---

## 6. Resumen de claves (`.env`)

- **`PERPLEXITY_SESSION_TOKEN`:** casi siempre necesaria para el núcleo.
- **`NOTION_TOKEN`:** solo con Notion activo en la misión.
- **`CURSOR_API_KEY`:** solo para pasos que llaman al CLI Cursor (`agent`).

---

## 7. Dónde leer más

- [README principal](../README.md) — instalación y comandos.
- [ESTADO_Y_OBJETIVO.md](ESTADO_Y_OBJETIVO.md) — visión y límites.
- [.cursorrules](../.cursorrules) — directivas `@` para el agente en el IDE.
