# Escenarios E2E manuales (operador)

Validación **de punta a punta** con APIs reales donde aplica: calidad del borrador y coherencia de artefactos la juzga **una persona**, no un único assert automático. Complementa la suite CI (`pytest -m "not integration and not notion_real"`).

**Prerrequisitos:** venv, `pip install -e ".[dev]"`, `.env` con `PERPLEXITY_SESSION_TOKEN` cuando el escenario no sea dry-run. Ver [.env.example](../.env.example).

---

## Matriz de escenarios

| ID | Objetivo | Flujo resumido | Criterios de éxito (mínimos) |
|----|----------|----------------|------------------------------|
| **M1** | Pipeline mínimo real | `mission.md` con 1–2 secciones y `max_perplexity_calls` bajo; `paper-pipeline mission.md` **sin** `--dry-run`. | Existen `outputs/<sección>.md`, `draft_paper.md`, `run.log` (JSONL) sin errores fatales; el borrador es legible. |
| **M2** | Estrategia Perplexity | `PAPER_PIPELINE_PERPLEXITY_STRATEGY=1` y misma corrida que M1 (o una sección). | `outputs/perplexity_call_record.jsonl` tiene al menos una línea con `query_hash` o perfil; no falla el pipeline. |
| **M3** | Hipervisor / triaje | Misión con `enable_hypervisor_triage: true` (u opciones alineadas al contrato), `metrics.json` válido si el triaje lo exige. | `outputs/triage/triage_report.json`; en Cockpit API `GET .../triage/latest` devuelve JSON; tier coherente con métricas. |
| **M4** | Modo autonomía (dry-run) | En `mission.md`: `mode: autonomy` (y opcional `autonomy:`). Ejecutar `paper-agent-step --output-dir <misión>/outputs` **o** `POST /api/missions/{id}/agent/run-step` con `{"dry_run": true}`. | Se añade línea a `outputs/agent_decisions.jsonl` con `dry_run: true`, bloques `safety` y `policy_pre`; **no** requiere `PAPER_PIPELINE_AUTONOMY_EXECUTE` para dry-run. |
| **M5** | Bloqueo por señales | Tras tener `objective_state.json`, forzar `gates.loop_stopped: true` **o** poner `metrics_validation_errors` en `triage/triage_report.json`; volver a ejecutar el paso autónomo (M4). | En la nueva línea de `agent_decisions.jsonl`, `safety.decision` es `BLOCK` y el `rule_id` es coherente ([`safety.py`](../paper_pipeline/agent/safety.py)). |
| **M6** | Cockpit en vivo | `paper-web` (o uvicorn); abrir `/missions/<id>/cockpit`. | Título “Cockpit — &lt;id&gt;”; bloques Ledger/Evidence cargan si existen artefactos; donde falte JSON, mensaje “—” sin tumbar la página. |

---

## Comandos de referencia

```bash
# CI / sin cuota
cd paper-pipeline
pytest -m "not integration and not notion_real" -q

# Humo Perplexity (consume cuota)
pytest tests/test_perplexity_integration.py -m integration -q
pytest tests/test_autonomy_integration.py -m autonomy_integration -q

# E2E Cockpit (requiere: npm run build en web/, Playwright Chromium)
pytest tests/test_cockpit_e2e.py -m cockpit_e2e -q
```

---

## Variables de entorno relevantes

| Variable | Uso en escenarios |
|----------|-------------------|
| `PERPLEXITY_SESSION_TOKEN` | M1, M2, M3 (y pruebas `integration` / `autonomy_integration`). |
| `PAPER_PIPELINE_PERPLEXITY_STRATEGY=1` | M2. |
| `PAPER_PIPELINE_DATA_DIR` | M6 si el servidor no usa `./data/missions` por defecto. |
| `PAPER_PIPELINE_AUTONOMY_EXECUTE=1` | Solo si probás `dry_run: false` y querés `would_execute: true` en `agent_decisions.jsonl`; **la ejecución real del pipeline tras ese flag no está cableada** en esta versión. |

---

## Líneas de investigación sugeridas (plantillas de misión)

Para evaluar **calidad** del texto y de la traza (no solo que el pipeline corra):

1. **Interpretabilidad mecánica / SAEs** — revisar `vision_futura/example_mech_interp_mission.md` y adaptar el frontmatter al contrato real de [`Mission`](../paper_pipeline/mission.py).
2. **Robustez de evaluación de LLM** — benchmarks, leakage, claims fuertes; secciones `gaps`, `methodology`, `related_work`.
3. **Reproducibilidad** — varianza, intervalos, reporting; encaja con `metrics.json` + triaje + `publish_decision`.
4. **Dominio acotado** (p. ej. detección con sensores) — bucles cortos con `paper-loop` y directivas `@`.

---

## Notas de implementación (SPA)

- El servidor sirve `web/dist` con **fallback a `index.html`** para rutas del cliente (p. ej. `/missions/:id/cockpit`), y monta `/assets` aparte. Las rutas más específicas de la API se registran antes que ese fallback ([`main.py`](../paper_pipeline/server/main.py)).
- En la app React, las rutas bajo `/missions/...` deben declararse **antes** que `path="/"` para que el enrutador no resuelva siempre el inicio ([`App.tsx`](../web/src/App.tsx)).

## Ver también

- [GUIA_PRUEBAS_Y_DEBUG.md](GUIA_PRUEBAS_Y_DEBUG.md) — depuración por capa.
- [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md) — flujo de comandos.
- [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md) — artefactos bajo `outputs/`.
