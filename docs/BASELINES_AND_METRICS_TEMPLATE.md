# Plantilla: baselines y métricas para un estudio serio

Copiá o adaptá esta tabla en tu apéndice o en `outputs/` como nota de trabajo (`outputs/study_baselines.md` manual).

## Tabla mínima (3 corridas)

| Config ID | Variante | Descripción | Claims verificados (%) | Intervenciones humanas | Errores por tipo (log) | Tiempo (min) | Coste LLM (llamadas) |
|-----------|----------|-------------|-------------------------|------------------------|------------------------|--------------|----------------------|
| B0 | Solo narrativo | Pipeline Perplexity sin código ejecutado | _rellenar_ | _rellenar_ | _rellenar_ | | |
| B1 | Pipeline + código | Mismo tema + `outputs/code/` + métricas en `metrics.json` | | | | | |
| B2 | Línea base manual / script fijo | Control humano o script determinista | | | | | |

## Métricas recomendadas (además de chars / duration / calls_used)

- **Tasa de claims con evidencia:** revisar `outputs/evidence/claims_evidence_checklist.json` y contar `evidence_status: verified` vs `unverified`.
- **Intervenciones:** ediciones manuales en `mission.md`, re-ejecuciones, correcciones en `cursor_turn.md` (conteo manual o bitácora).
- **Errores por tipo:** agrupar entradas en `run_state.json` / logs por `perplexity_call_failed`, validación de sección, etc.

## Relación con el triaje

Si `metrics.json` está alineado con [mvp_metrics_example.json](../paper_pipeline/schemas/mvp_metrics_example.json), el hipervisor puede clasificar tiers según [HIPERVISOR_Y_PARALELO.md](HIPERVISOR_Y_PARALELO.md).
