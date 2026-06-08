# Referencia de `outputs/`

Cada archivo indica **quién lo escribe**, **cuándo existe** y **qué implica si falta**.

```
outputs/
│
├── <sección>.md              ← `paper-pipeline` (una llamada Perplexity por sección en `sections_needed`)
│                                o `paper-loop` tras `@PERPLEXITY:<sección>`.
│                                Condición: se generó tras una llamada exitosa (no dry-run).
│                                Si falta: la sección no se llegó a generar (cupo, error, o aún no ejecutado).
│
├── draft_paper.md            ← `paper-pipeline` al final del flujo; `paper-loop` tras `@PERPLEXITY` si hubo rebuild.
│                                Condición: ejecución real (no `--dry-run` en `paper-pipeline`). Suele existir si al
│                                menos una sección `.md` se escribió; si todas las claves son desconocidas, puede
│                                quedar casi solo la cabecera.
│                                Si falta: el proceso terminó antes del ensamblado o fue solo dry-run.
│
├── quality_gaps.md           ← `paper-pipeline`, paso quality check.
│                                Condición: `enable_quality_check: true` **y** quedaba cupo
│                                (`calls_used < max_perplexity_calls`) antes del quality check.
│                                Si falta y lo esperabas: revisá `max_perplexity_calls` o desactivaste el check.
│
├── code/README.md            ← `paper-pipeline` si `code_needed: true`.
│                                Condición: solo con esa bandera en `mission.md`.
│
├── cursor_turn.md            ← Lo creás o ampliás vos; **entrada/salida** del bucle reactivo.
│                                `paper-loop` **lee** directivas `@` y **borra** los bloques ejecutados.
│                                Si tras ejecutar siguen `@`: fallo de parseo o encoding (UTF-8 sin BOM).
│
├── next_instruction.md       ← `paper-meta-loop` / `paper-meta-watch` (revisor Perplexity).
│                                Contiene CONTINUE o STOP + texto. `paper-loop` lo lee al inicio de cada ciclo.
│
├── meta_loop_log.md          ← Anotaciones por ronda del meta-loop (append).
├── meta_loop_state.json      ← Ronda actual y decisión (meta-loop; distinto de `run_state.json` del pipeline).
│
├── notion_sync.log           ← Resultado del sync Notion o mensaje de “omitido / deshabilitado”.
│
├── run.log                   ← **JSONL** (un JSON por línea): eventos `step_*`, duraciones, errores estructurados.
│                                Escrito por el orquestador y el bucle integrado cuando el logging estructurado está activo.
│
├── run_ledger.json           ← **Estado canónico del run** (fases, integraciones, decisión). Preferí este archivo
│                                frente a reconstruir solo desde `manifest.json` o `run.log`.
│
├── preflight_report.json     ← Comprobaciones de entorno/paths antes de gastar cuota (token, permisos).
│
├── validation/quality_validation.json ← Resultado de *quality gates* (estructural + informes).
├── validation/experiment_deterministic.json ← Validación determinista de ``metrics.json`` (exit_code, finitud numérica, cotas opcionales) cuando corre el bucle post-Cursor; ver ``experiment_metrics_validate.py``.
│
├── evidence/                 ← Índice de evidencia (`evidence_index.json`, `claims.json`, `claims_evidence_checklist.json`, etc.).
│                                `claims_evidence_checklist.json` lista candidatos a claims con `evidence_status` (p. ej. `unverified`)
│                                para revisión humana o externa; ver [technical/EVALUATION_LAYERS.md](technical/EVALUATION_LAYERS.md).
│
├── publication/publish_decision.json ← Elegibilidad de publicación (`compute_publish_signals`: quality + triage; ver `publication/signals.py`).
│
├── metrics.json              ← Métricas numéricas para el hipervisor; validación estricta `MetricsBundle` antes del triaje
│                                (`paper_pipeline/evidence/metrics_io.py`). Opcional: `PAPER_PIPELINE_RELAX_METRICS=1` para un
│                                segundo parse permisivo documentado en [HIPERVISOR_Y_PARALELO.md](HIPERVISOR_Y_PARALELO.md).
│                                Si `experiment_runner.iteration_after_cursor: true`, puede generarse **solo** tras el bucle post-Cursor (no al inicio del run).
│
├── triage/triage_report.json ← Tier, motivo, métricas; puede incluir `metrics_validation_errors` o `metrics_relax_mode`.
├── triage/events.jsonl       ← Una línea JSON por ejecución de triaje.
│
├── loop/loop_state.json      ← Escrito por **`paper-loop`** cuando persiste estado entre ciclos (hash/chars del borrador, racha de stalls).
├── loop/stop_decision.json   ← Si el bucle detecta degradación (p. ej. `LOOP_STALL_DETECT=1`), política de parada + `ExitCode.LOOP_STALLED` (8).
│
├── safety_trace.jsonl        ← Trazas append-only de decisiones de gobernanza (`SafetyController`): `ALLOW`,
│                                `REQUIRE_HUMAN_APPROVAL` o `BLOCK`, con `rule_id`, razones y artefactos fuente.
│                                Lo escriben actualmente `publish_manager`, `integrated_loop_main` y `orchestrator_v2`.
│
├── objective_state.json      ← Estado derivado de la función objetivo V1: resume utilidad total, términos,
│                                gates (`metrics_valid`, `publishable`, `loop_stopped`, `requires_human_approval`)
│                                y artefactos usados para la consolidación. Lo escriben `runner`, `orchestrator_v2`
│                                e `integrated_loop_main`.
├── objective_trace.jsonl     ← Traza append-only del scoring de `ObjectiveState`: familia de acción, utilidad,
│                                términos, gates y resumen de decisión.
│
├── research_memory.jsonl     ← Memoria episódica mínima de investigación. Cada línea guarda un evento de valor alto
│                                (`quality`, `triage`, `publish`, `loop_stop`, `run_consolidation`) con resumen,
│                                confianza y `source_artifacts`.
├── memory_index.json         ← Índice barato regenerable desde `research_memory.jsonl`: contadores por tipo,
│                                último evento y última entrada por `kind`, pensado para Cockpit/API.
│
├── goal_selection.json       ← Recomendación estructurada del siguiente paso (`literature`, `verification`,
│                                `writing`, `experiment`, `wait_human`, `stop`) derivada de `objective_state.json`
│                                y `memory_index.json`. La escriben `runner`, `orchestrator_v2` e
│                                `integrated_loop_main`.
│
├── perplexity_call_record.jsonl ← Append-only (opcional): si `PAPER_PIPELINE_PERPLEXITY_STRATEGY=1`, una línea
│                                JSON por llamada Perplexity planificada en `perplexity_phase` (perfil, modo,
│                                `query_hash`, modelo). Ver `docs/technical/perplexity-strategy-spec.md`.
│
├── agent_decisions.jsonl     ← Append-only: un paso del scheduler (`run_agent_step` / API `POST .../agent/run-step`):
│                                `dry_run`, `selected_goal_type`, decisión `SafetyController`, `policy_pre` / `policy_post`,
│                                `would_execute` (requiere `mode: autonomy`, gates OK y `PAPER_PIPELINE_AUTONOMY_EXECUTE`).
│                                Ver `paper_pipeline/agent/scheduler.py`.
│
├── goals.json                ← Árbol de metas V1 (`GoalNode`: id, parent_id, description, goal_type, status). Semilla
│                                automática si falta (`ensure_goals_seed`). Si hay un nodo `in_progress`, la selección
│                                de siguiente paso lo respeta. Ver `paper_pipeline/agent/goals.py`.
│
├── working_memory.json       ← Snapshot del último `GoalSelection` (working memory del ciclo). `strategic_memory.py`.
│
├── hypotheses_registry.json  ← Lista de hipótesis con estado (V2 thin; puede arrancar vacía). `strategic_memory.py`.
│
├── research_pack/            ← Solo si publicación elegible y `PAPER_PIPELINE_BUILD_PACKS=1` (copia selectiva para zip).
├── code_pack/MANIFEST.md     ← Manifiesto opcional con `git rev-parse HEAD` si aplica.
│
├── run_state.json            ← Estado resumible del `paper-pipeline`: secciones ya completadas, pasos opcionales.
│                                Permite reanudar sin repetir secciones si el proceso se interrumpe.
│                                Si `single_thread_perplexity: true` en la misión, también guarda `perplexity_backend_uuid`
│                                y `perplexity_read_write_token` para seguir el mismo hilo al reanudar.
│
├── cursor_cli.log            ← Traza del agente Cursor (SDK streaming o CLI subprocess); append por intento si hay reintentos.
├── cursor_cli_diagnostics.json ← Último diagnóstico (comando/modelo, stderr/stdout truncados, `backend`, `run_id`, `agent_id` en SDK).
├── cursor_cli_rounds.json    ← Lista de intentos (`process_returncode`, `backend`, `run_id`, …) si hubo reintentos.
├── cursor_agent_state.json   ← Persistencia SDK: `agent_id`, `model`, `cwd` para `Agent.resume` en la siguiente invocación.
├── cursor_cli_prompt_last.txt ← Último prompt enviado (SDK o stdin CLI en Windows/prompts largos).
├── experiment_iteration.jsonl ← Una línea JSON por ronda del bucle post-Cursor (experimento + validación determinista).
├── experiment_iteration_hint.md ← Pista generada tras fallo de validación o experimento; alimenta el siguiente ``cursor_cli`` en ese bucle.
├── INTEGRATION_TRANSCRIPT.md ← Append de trazas (p. ej. Cursor CLI) vía ``integration_transcript.append_transcript``; no confundir con ``cursor_turn.md``.
└── (otros .md)               ← Secciones extra generadas en el loop con nombres no listados en `mission.md`
                                   se incluyen en `draft_paper.md` al rebuild.
```

## Relación entre `meta_loop_state.json` y `run_state.json`

- **`meta_loop_state.json`**: solo el **meta-agente** (rondas, CONTINUE/STOP).
- **`run_state.json`**: **pipeline principal** (secciones Perplexity y pasos como quality / notion / cursor).

Son complementarios; no se fusionan en una sola estructura en esta versión.

## Ver también

- [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md) — flujo de comandos y bucles.
- [ESTADO_Y_OBJETIVO.md](ESTADO_Y_OBJETIVO.md) — alcance y limitaciones del proyecto.
- [technical/safety-policy-spec.md](technical/safety-policy-spec.md) — política y formato de `safety_trace.jsonl`.
- [technical/objective-spec.md](technical/objective-spec.md) — fórmula y trazas de `ObjectiveState V1`.
- [technical/memory-spec.md](technical/memory-spec.md) — contrato y límites de `ResearchMemory V1`.
- [technical/goal-selection-spec.md](technical/goal-selection-spec.md) — contrato y límites de `Goal Selection V1`.
