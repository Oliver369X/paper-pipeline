# Figuras para documentación y preprint (P4)

## Fuentes Mermaid (`.mmd`)

| Archivo | Contenido |
|---------|-----------|
| [architecture_overview.mmd](architecture_overview.mmd) | CLI / Web → `runner` → integraciones (sincronizado con [technical/01-arquitectura.md](../technical/01-arquitectura.md)) |
| [architecture_governance.mmd](architecture_governance.mmd) | Ledger, señales de publicación, `agent_eval` (complemento conceptual; no todos los edges existen como llamadas directas en código) |
| [case_study_replication_flow.mmd](case_study_replication_flow.mmd) | Misión → `outputs/` → export `case_study_trace.json` / appendix (alineado al preprint §5) |

## Exportar a PNG / SVG (LaTeX, slides)

Requisito: [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) (`npm install -g @mermaid-js/mermaid-cli`).

Desde la raíz del repo `paper-pipeline`:

**Windows (PowerShell):**

```powershell
.\scripts\export_architecture_figure.ps1
```

**Linux / macOS:**

```bash
bash scripts/export_architecture_figure.sh
```

Salida por defecto: `docs/assets/generated/` (crear el directorio si no existe). Los binarios **no** están versionados obligatoriamente; regeneralos antes de incluir el paper.

## Sincronización con la doc

Si editás el diagrama “Vista general” en `01-arquitectura.md`, actualizá también `architecture_overview.mmd` para que sigan siendo la misma figura.
