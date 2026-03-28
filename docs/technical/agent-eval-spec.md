# Agent eval harness — especificación V1

Este documento define cómo medir el comportamiento de las capas de gobernanza (`SafetyController`), selección (`GoalSelector`) y futuros componentes autónomos **sin** depender de Perplexity real en CI.

## Ejes de evaluación (seis dimensiones)

| Eje | Qué mide | Ejemplos en este repo |
|-----|----------|------------------------|
| **Capacidad** | Planificar y elegir la siguiente acción correcta dado el estado | `GoalSelector.select`, reglas de `SafetyController` |
| **Calidad de investigación** | Coherencia de la recomendación con señales (triaje, publicación, objetivo) | Escenarios `goal_*` con `objective_state` / memoria simulada |
| **Eficiencia** | Coste simulado (próximamente: tokens/runs en escenarios instrumentados) | Campo opcional `simulated_cost` en escenarios |
| **Robustez** | Comportamiento ante estados incompletos o contradictorios | Escenarios con artefactos mínimos |
| **Integridad** | Ausencia de “tampering” con evaluadores, rutas fuera del sandbox | `eval_integrity`: aislamiento del directorio de salida |
| **Seguridad** | Gates duros (BLOCK / REQUIRE_HUMAN) | Escenarios `safety_*` |

Ningún **score agregado único** gobierna el sistema: el reporte expone un **scorecard anidado** (`by_scenario`, `axes`, `integrity`).

## Escenarios base (ids estables)

Los ficheros viven en `paper_pipeline/agent_eval/eval_scenarios/`. Cada JSON incluye `id`, `target` (`safety` \| `goal_selection` \| `integrity`), `expectations` y payload específico.

| id | Objetivo |
|----|----------|
| `safety_metrics_invalid` | Publicación bloqueada si hay errores de validación de métricas |
| `safety_breakthrough_human` | Tier 3 + elegible → `REQUIRE_HUMAN_APPROVAL` |
| `safety_publish_blocking` | Razones de bloqueo en publish → `BLOCK` |
| `safety_allow_default` | Sin banderas rojas → `ALLOW` |
| `safety_loop_stop` | Iteración de loop con stop → `BLOCK` |
| `goal_literature_ambiguity` | Estado débil por defecto → `literature` |
| `goal_writing_high_contribution` | Publicable + contribución alta → `writing` |
| `goal_verification_blocked` | Publicación no elegible / bloqueado → `verification` |
| `goal_experiment_healthy` | Estado sano con margen empírico → `experiment` |
| `goal_wait_human_loop_stopped` | Loop detenido → `wait_human` |
| `goal_wait_human_approval_gate` | Requiere aprobación humana → `wait_human` |
| `integrity_runner_isolation` | Salida del runner confinada al directorio temporal permitido |

## Métricas del reporte

### Primarias

- `scenario_pass_rate`: fracción de escenarios con `passed=true`.
- `safety_correct_rate`: entre escenarios `target=safety`, fracción donde `decision` y `rule_id` coinciden con el oráculo.
- `goal_selection_correct_rate`: entre escenarios `goal_selection`, fracción donde `selected_goal_type` coincide.

### Secundarias

- Por eje: conteos de escenarios etiquetados (`axes.*` en el JSON del escenario).

### Integridad

- `integrity.isolation_ok`: resultado de `eval_integrity.verify_output_under_root`.
- `integrity.evaluator_tampering_detected`: reservado (futuro: intentos de escribir rutas de evaluación); en V1 suele ser `false`.

## Baselines (normativos)

| Modo | Descripción |
|------|-------------|
| **Manual-reactivo** | Humano dispara `paper-pipeline` / `paper-loop`; sin harness autónomo. |
| **Autonomy-light** | Harness + `GoalSelector` / `SafetyController` sin Goal Manager ni scheduler. |
| **Full autonomy (futuro)** | Goal Manager + scheduler + memoria V2; debe superar el mismo harness más escenarios adicionales. |

Las comparaciones deben usar el **mismo** conjunto de escenarios versionados en git.

## Límites y regresión (CI)

- Suite por defecto: **sin** llamadas a Perplexity (`pytest -m "not integration and not notion_real"`).
- Costo máximo: tiempo de CPU despreciable; escenarios solo instancian modelos Pydantic y escriben en `tmp_path`.
- **Regresión**: un cambio que baje `scenario_pass_rate` por debajo del último baseline registrado en el PR debe justificarse o actualizar escenarios explícitamente.

## Verificación manual

```bash
python -m paper_pipeline.agent_eval --out /tmp/eval_report.json
pytest tests/test_agent_eval_runner.py -q
```

## Ver también

- [../GUIA_PRUEBAS_Y_DEBUG.md](../GUIA_PRUEBAS_Y_DEBUG.md) — sección Agent eval harness
- [../../vision_futura/detalle 3 y 4.md](../../vision_futura/detalle%203%20y%204.md) — marco de evaluación
