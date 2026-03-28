# Hipervisor de triaje y ejecución en paralelo (worktrees)

> **Resumen técnico corto:** [technical/05-paralelo-triage.md](technical/05-paralelo-triage.md).  
> **Índice de docs:** [README.md](README.md).

Este documento describe lo **implementado** en código (no solo la visión de `vision_futura/`).

## 1. Tiers (clasificación)

| Tier | Significado (resumen) |
|------|------------------------|
| 0 | Crash: `exit_code ≠ 0`, OOM, cobertura &lt; 50 % |
| 1 | Refutado: métrica peor que baseline SOTA con `math_checks: PASS` (resultado negativo honesto) |
| 2 | Cerca del SOTA: dentro de `quality_gates.replication_tolerance` |
| 3 | Breakthrough: métrica supera baseline + `breakthrough_margin`, o `anomaly_detected: true` |

**No se borran ramas desde este módulo** — los artefactos van a disco; opcionalmente, en tier 3 y con variables de entorno, se puede **añadir una sección en Notion** vía API REST (véase [NOTION_MCP_TRIAGE.md](NOTION_MCP_TRIAGE.md)).

## 2. `outputs/metrics.json`

El experimento (o un harness) puede dejar métricas para el triaje:

```json
{
  "exit_code": 0,
  "main": 0.85,
  "baseline": 0.80,
  "coverage": 0.92,
  "math_checks": "PASS",
  "anomaly_detected": false,
  "oom_error": false
}
```

Los umbrales por defecto vienen de `mission.md` → `quality_gates` (`sota_baseline_value`, `breakthrough_margin`, `replication_tolerance`, `higher_is_better`).

### Métricas inválidas

Si existe `outputs/metrics.json` pero **no** cumple el contrato Pydantic `MetricsBundle` (véase `paper_pipeline/evidence/metrics_model.py` y `schemas/metrics.schema.json`), el triaje **no** clasifica como tier 3: se escribe tier **0** con etiqueta `invalid_metrics` y el campo `metrics_validation_errors` en `triage/triage_report.json` con los mensajes de validación. JSON antiguo **sin** `schema_version` se acepta asumiendo `schema_version: 1`. Un ejemplo válido está en `examples/metrics.valid.json`.

**Modo relax (solo transición / legacy):** si defines **`PAPER_PIPELINE_RELAX_METRICS=1`** (`true` / `yes`) y el JSON **sigue pudiendo parsearse** como `TriageMetrics` (modelo más permisivo que `MetricsBundle`), el triaje **continúa** con la clasificación normal y se guardan `metrics_relax_mode: true` y `metrics_bundle_strict_errors` en el reporte para auditoría. Si ni siquiera `TriageMetrics` valida, se mantiene tier 0. No usar en producción salvo migración controlada.

## 3. Artefactos generados

Con `enable_hypervisor_triage: true` en la misión y **después** de un run real (no `dry_run`):

- `outputs/triage/triage_report.json` — tier, etiqueta, motivo, detalle.
- `outputs/triage/events.jsonl` — una línea JSON por cada triaje (auditoría local; apto para ingestión posterior a Notion/ELK).
- `outputs/triage/FAILURES.md` — solo si el tier es **1** (autopsia legible).

Si no existe `metrics.json`, el triaje no escribe nada (solo log informativo).

### Webhook en breakthrough (tier 3)

Si defines la variable de entorno **`PAPER_PIPELINE_TRIAGE_WEBHOOK_URL`** (URL HTTPS), en clasificación **tier 3** se hace un `POST` JSON con campos como `event`, `tier`, `topic`, `output_dir`, `metrics`, `ts`. Los fallos de red **no** abortan el pipeline (solo log de advertencia).

### Notion en breakthrough (tier 3)

Si defines **`NOTION_TOKEN`** y **`NOTION_TRIAGE_PAGE_ID`** (página compartida con la misma integración que uses para el Notion MCP en Cursor), en tier 3 se **añade un bloque** a esa página con resumen del breakthrough. Mismo token que el resto del pipeline y que el MCP; detalles en [NOTION_MCP_TRIAGE.md](NOTION_MCP_TRIAGE.md).

## 4. CLI `paper-parallel`

Tras `pip install -e .`:

```bash
# Clasificar a partir de mission + outputs (métricas ya presentes)
paper-parallel triage --mission mission.md --output-dir outputs

# Lote de worktrees (JSON con specs; requiere repo git)
paper-parallel batch --repo . --specs specs.json
```

`specs.json` es un array de objetos con al menos `exp_id`, `mission_md_content`, y opcionalmente `command` (lista de strings), `hypothesis`, `branch_name`.

## 5. Integración pipeline v2

En `mission.md`:

```yaml
enable_hypervisor_triage: true
```

`run_pipeline_v2` (CLI `--v2` y API web) ejecuta el triaje al final si hay métricas.

## 6. Worktrees paralelos

`paper_pipeline.parallel.worktree_runner.ParallelWorktreeOrchestrator` crea worktrees aislados. Si tras el comando del agente existe `outputs/metrics.json` y la misión en el worktree tiene `enable_hypervisor_triage: true`, se calcula el tier y se rellena `spec.tier_result` (p. ej. para conservar rama en breakthrough si `keep_breakthrough_branches`).

## 7. Próximos pasos (opcionales)

- Webhook ya cubre Slack/Discord vía *Incoming Webhook* o un relay propio.
- Notion opcional en tier 3 vía REST ([NOTION_MCP_TRIAGE.md](NOTION_MCP_TRIAGE.md)); ingestión adicional desde `events.jsonl` si quieres tablas o automatizaciones propias.
- Cola de `git push` multi-agente más allá del commit serializado actual.
