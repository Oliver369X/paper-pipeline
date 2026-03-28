# Misión: juego 3D de carreras (bucle Cursor)

## Ubicación del juego

Tras ejecutar el bucle, el código queda en:

`missions/racing_game_3d/outputs/code/X/`

(abre `index.html` con un servidor estático; ver README dentro de `X`).

## Requisitos

- Python con `paper-pipeline` instalado (`pip install -e .` desde `paper-pipeline/`).
- [Cursor CLI](https://cursor.com/docs/cli/headless): el comando `agent` en PATH (o `CURSOR_AGENT_BIN` al `.exe` en Windows).
- `CURSOR_API_KEY` en `paper-pipeline/.env` (o en el entorno).

## Modelo Composer 2 Fast

En `paper-pipeline/.env`:

```env
CURSOR_API_KEY=tu_key
CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast
```

## Comando

Desde la carpeta `paper-pipeline/` (con venv activado):

**PowerShell**

```powershell
cd paper-pipeline
.\.venv\Scripts\Activate.ps1
$env:CURSOR_AGENT_EXTRA_ARGS="--model composer-2-fast"
paper-racing-loop missions/racing_game_3d/mission.md
```

**Probar sin llamar al agente**

```powershell
paper-racing-loop missions/racing_game_3d/mission.md --dry-run
```

**Menos rondas (p. ej. 3)**

```powershell
paper-racing-loop missions/racing_game_3d/mission.md --rounds 3
```

## Logs

Salida del CLI de Cursor: `missions/racing_game_3d/outputs/cursor_cli.log` y apéndices en `cursor_turn.md`.
