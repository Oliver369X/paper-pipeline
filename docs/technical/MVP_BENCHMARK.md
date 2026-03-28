# MVP: benchmark ejecutable mínimo (especificación)

Objetivo: un único experimento **cerrado** que produzca números en disco y pueda alimentar `outputs/metrics.json` (hipervisor / triaje).

## Contrato sugerido

Tras ejecutar código (manual o CI), escribir o fusionar en `outputs/metrics.json`:

```json
{
  "schema_version": 1,
  "mvp_benchmark": {
    "name": "example_mnist_baseline",
    "status": "ok",
    "main": 0.97,
    "metric_name": "accuracy",
    "higher_is_better": true,
    "notes": "single run, seed fixed"
  }
}
```

Alinear `main`, `metric_name`, `higher_is_better` con [QualityGatesConfig](../../paper_pipeline/mission.py) en la misión si usás gates.

## Ejemplo de archivo

Ver [mvp_metrics_example.json](../../paper_pipeline/schemas/mvp_metrics_example.json).

## Relación con el pipeline Perplexity

El pipeline **lineal** no ejecuta este benchmark solo: hace falta correr scripts bajo `outputs/code/` o un job externo y volcar métricas. El borrador narrativo y los números reales deben **coincidir** explícitamente (revisión humana).
