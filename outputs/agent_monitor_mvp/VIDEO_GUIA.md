# Guion sugerido para vídeo de auditoría (5–10 min)

1. **Entorno (sin secretos):** mostrar que existen variables `PERPLEXITY_SESSION_TOKEN` y `CURSOR_API_KEY` sin expandir valores; mencionar `CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast`.
2. **Tests:** ejecutar Fase A (`pytest` con `--ignore` de integración como en `AUDITORIA.md`).
3. **Un ciclo real corto:** `paper-loop` con `--max-cycles 1` (sin dry-run) o solo `paper-meta-loop` + `paper-cursor-agent` según prefieras.
4. **Evidencia:** abrir `meta_loop_log.md`, `perplexity_meta_audit.md`, fragmento de `cursor_cli.log`.
5. **Producto:** servir `code/monitor` con `python -m http.server`, mostrar mapa y filtros.

Exportar el vídeo con el mismo nombre que la carpeta del proyecto o subirlo al almacén que uses para entregas.
