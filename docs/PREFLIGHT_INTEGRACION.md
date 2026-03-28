# Pre-vuelo: integración Perplexity + Cursor (Composer 2 Fast)

## 1. Cursor CLI

- Comprobar instalación: `agent --version` y `agent models`.
- Modelo objetivo del plan: **Composer 2 Fast** → id listado: `composer-2-fast`.
- Variable de entorno (mismo proceso que ejecuta `paper-cursor-agent` / `paper-loop`):

  ```text
  CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast
  ```

- El comando construido por el pipeline es equivalente a:  
  `agent -p --force --output-format text --model composer-2-fast "<prompt>"`

## 2. Perplexity

- `PERPLEXITY_SESSION_TOKEN`: cookie `__Secure-next-auth.session-token` de la cuenta que usarás en la web.
- Modelo del plan: **`claude-sonnet-4.6-thinking`** en `mission.md` (también default de `paper-meta-loop`).

## 3. Windows

- Si falla el spawn: `CURSOR_AGENT_BIN` con ruta absoluta al `agent.exe` (`where agent`).

## 4. Degradación

- Si `--model composer-2-fast` no es aceptado por tu versión de `agent`, quitá `CURSOR_AGENT_EXTRA_ARGS` y documentá la degradación en `outputs/.../AUDITORIA.md`.
