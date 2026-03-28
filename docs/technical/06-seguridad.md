# 06 — Seguridad

## Identificadores de misión

API: validación en `server/paths.py` para evitar path traversal en `mission_id`.

## Comandos en paralelo

- `command_safety.py`: patrones peligrosos (`rm -rf /`, subshells, etc.).
- Prefijos permitidos por entorno o lista por defecto.

## Secretos

- No commitear `.env`.
- Tokens solo en variables de entorno o almacén seguro del host.

## Cursor / subprocess

- Timeouts y logs en `cursor_cli_runner` (revisar `run.log` para fallos).
