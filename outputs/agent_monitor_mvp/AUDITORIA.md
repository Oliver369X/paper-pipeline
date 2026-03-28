# Auditoría — integración Perplexity + Cursor (agent monitor MVP)

## Resumen ejecutivo

| Campo | Valor |
| ----- | ----- |
| Objetivo | SPA solo-frontend (mapa + datos demo) y bucle ≥5 interacciones Perplexity ↔ Cursor trazables |
| Resultado global | **Implementación repo completada** · integración en vivo **pendiente de ejecutar** con `PERPLEXITY_SESSION_TOKEN` y `CURSOR_API_KEY` en el entorno del operador |
| Modelo Perplexity | `claude-sonnet-4.6-thinking` (mission + meta-loop) |
| Modelo Cursor | `composer-2-fast` vía `CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast` |

## Pruebas por fases (registro)

### Fase A — Automatizada (sin integración externa opcional)

Comando ejecutado en CI local:

```bash
python -m pytest -q --tb=short --ignore tests/test_perplexity_integration.py --ignore tests/test_cursor_cli_integration.py
```

**Resultado:** 48 passed (2026-03-24). Los tests `test_perplexity_integration` y `test_cursor_cli_integration` quedan excluidos porque requieren token/credenciales/binario en PATH específicos.

### Fase B — Orquestación en seco

```bash
python -m paper_pipeline.integrated_loop_main missions/agent_monitor_mvp/mission.md --output-dir outputs/agent_monitor_mvp --dry-run --max-cycles 6 --no-meta
```

**Resultado:** exit 0; se detecta 1 directiva `@CURSOR` por ciclo en `next_instruction.md`.

### Fase C — Integración real (rellenar tras ejecutar)

| Paso | Comando | Pass/Fail | Notas |
| ---- | ------- | --------- | ----- |
| C1 | `paper-loop ... --max-cycles 6` con tokens | pendiente | Ver `missions/agent_monitor_mvp/README.md` |
| C2 | Verificar ≥5 rondas en `meta_loop_log.md` y trazas en `cursor_cli.log` | pendiente | |

### Fase D — Aceptación SPA (manual)

| Criterio | Pass/Fail |
| -------- | --------- |
| `python -m http.server` desde `code/monitor`, mapa visible | pendiente (estructura entregada en repo) |
| `data/events.json` carga sin error en consola | pendiente |

## Cambios de código relevantes (repo)

- `meta_loop.py`: reanudación de hilo Perplexity (`resume_conversation`), `next_instruction.md` con bloque `@CURSOR` automático en CONTINUE, `perplexity_meta_audit.md`.
- `integrated_loop.py`: meta-loop usa `mission.model`.
- `meta_main.py`: default `--model claude-sonnet-4.6-thinking`.
- Tests: `test_meta_loop_mocked.py` actualizado + `test_meta_loop_resumes_perplexity_thread`.

## Tabla de rondas (rellenar tras Fase C)

| Ronda | ISO timestamp | Decisión | backend_uuid Perplexity | Evidencia Cursor |
| ----- | --------------- | -------- | ------------------------ | ------------------ |
| 1 | | | | `cursor_cli.log` |
| 2 | | | | |
| … | | | | |

## Fallos y recuperación (matriz F#)

| F# | Ocurrió | Acción | Resultado |
| -- | ------- | ------ | --------- |
| — | — | — | Sin incidencias registradas en implementación |

*(Añadir filas si falla token, 401, timeout, etc.)*

## Modelos (sin secretos)

- Perplexity: `claude-sonnet-4.6-thinking`
- Cursor CLI extra args documentados: `--model composer-2-fast` (ver `docs/PREFLIGHT_INTEGRACION.md`)

## Historiales y artefactos

| Archivo | Uso |
| ------- | --- |
| **`INTEGRATION_TRANSCRIPT.md`** | **Historial único cronológico** (append automático): cada respuesta Perplexity meta-loop + cada salida Cursor CLI |
| `next_instruction.md` | Directivas `@CURSOR` / semilla |
| `cursor_turn.md` | Salida agregada por Cursor CLI (detalle) |
| `meta_loop_log.md` | Decisiones por ronda |
| `meta_loop_state.json` | Ronda + UUID Perplexity para resume |
| `perplexity_meta_audit.md` | Resumen por ronda Perplexity |
| `cursor_cli.log` | stdout/stderr agent completos |
| `run.log` | JSONL pipeline (si aplica) |

Si `INTEGRATION_TRANSCRIPT.md` no existe o está casi vacío, **aún no se ejecutó** integración real con tokens (`paper-loop` / `paper-meta-loop` + Cursor) en esa carpeta de salida.

## Vídeo (entrega manual)

Ver `VIDEO_GUIA.md` en esta carpeta.
