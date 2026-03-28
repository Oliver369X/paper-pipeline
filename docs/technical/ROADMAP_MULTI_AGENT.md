# Roadmap: arquitectura multi-agente iterativa (fuera del pipeline lineal actual)

## Estado actual

El núcleo productivo es **secuencial:** Perplexity por sección → ensamblado → calidad opcional ([runner.py](../../paper_pipeline/pipeline/runner.py)). Eso es un **orquestador de texto**, no un bucle planificar–actuar–observar con herramientas obligatorias.

## Dirección objetivo (si hay presupuesto de ingeniería)

1. **Estado compartido explícito** (plan, artefactos, métricas, errores tipados) entre pasos.
2. **Roles separados** (planificador, ejecutor de código, crítico con modelo o reglas **externas** al generador principal).
3. **Presupuesto** de tokens/llamadas con ramificación y **reintentos** justificados en log.
4. **No** duplicar el pipeline Perplexity actual: convive como modo «narrativo rápido»; el modo agente sería opt-in (`mission` flag o CLI distinto).

## Integración con el repo existente

- Modo `autonomy` y `paper-loop` / Cursor CLI son **piezas** hacia más control humano y herramientas; siguen sin sustituir un diseño multi-agente completo.
- Ver [MODE_NARRATIVE_VS_EMPIRICAL.md](../MODE_NARRATIVE_VS_EMPIRICAL.md) y [EVALUATION_LAYERS.md](EVALUATION_LAYERS.md).
