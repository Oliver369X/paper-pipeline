# autoresearch (Karpathy)

## Patrón principal

Agente mínimo (~630 líneas) que edita script de entrenamiento, corre experimentos overnight y evalúa métricas.

## 3 ideas adoptables

1. Bucle edit-run-measure ya parcial en `experiment_runner` + Cursor CLI.
2. Hipótesis → cambio de código → métrica en `metrics.json`.
3. Presupuesto de tiempo/coste en `SafetyConfig`.

## Archivos fuente

- `research-repos/autoresearch/train.py`
- `research-repos/autoresearch/program.md`

## Mapeo paper-pipeline

- `pipeline/experiment_phase.py`
- `pipeline/experiment_iteration.py`

## Riesgo / limitación

Específico a ML training; no generaliza a papers narrativos puros.

## Prioridad

P1
