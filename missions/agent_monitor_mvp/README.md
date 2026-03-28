# Agent Monitor MVP — guía de ejecución

## Pre-vuelo

1. Copiar `.env.example` a `paper-pipeline/.env` y definir:
   - `PERPLEXITY_SESSION_TOKEN`
   - `CURSOR_API_KEY`
   - `CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast` (verificado con `agent models` / `agent --help`)
   - Opcional: `CURSOR_AGENT_BIN` ruta absoluta al `agent.exe` en Windows.

2. Documentación adicional: [docs/PREFLIGHT_INTEGRACION.md](../../docs/PREFLIGHT_INTEGRACION.md).

## Comandos (desde `paper-pipeline/`)

```powershell
# Fase A — tests (sin red para la mayoría)
python -m pytest -q --tb=short

# Fase B — orquestación en seco
paper-loop missions/agent_monitor_mvp/mission.md --output-dir outputs/agent_monitor_mvp --dry-run --max-cycles 6 --no-meta

# Fase C — bucle real (requiere tokens)
paper-loop missions/agent_monitor_mvp/mission.md --output-dir outputs/agent_monitor_mvp --max-cycles 6 --goal "Construir SPA solo-frontend bajo outputs/agent_monitor_mvp/code/monitor con Leaflet y data/events.json demo; iterar mejoras de UI/mapa en cada ronda hasta checklist OK."
```

El meta-loop escribe `next_instruction.md` con `@CURSOR` automáticamente tras cada ronda Perplexity (mismo hilo si existe `meta_loop_state.json`).

## Servir la SPA

```powershell
Set-Location outputs/agent_monitor_mvp/code/monitor
python -m http.server 8765
```

Abrir `http://127.0.0.1:8765/`.

## Evidencias

- **`INTEGRATION_TRANSCRIPT.md`** — historial único (Perplexity + Cursor), generado por el pipeline al ejecutar meta-loop y Cursor CLI.
- `run.log`, `cursor_turn.md`, `next_instruction.md`, `meta_loop_log.md`, `cursor_cli.log`, `perplexity_meta_audit.md`, `AUDITORIA.md`.
