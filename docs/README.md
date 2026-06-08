# Documentación — paper-pipeline

Índice único para orientarte sin duplicar contenido: cada archivo tiene un propósito distinto.

## Lectura por rol

| Si querés… | Empezá por |
|------------|------------|
| Visión de producto, límites y qué está probado | [ESTADO_Y_OBJETIVO.md](ESTADO_Y_OBJETIVO.md) |
| Resumen 31-03: ejemplo para mostrar, misión vs paper vs baseline, todo lo implementado | [actualizacion-31-3.md](actualizacion-31-3.md) |
| Plan “v2 preprint” (esqueleto propuesto) vs estado real del repo | [ESTADO_PLAN_PREPRINT_V2.md](ESTADO_PLAN_PREPRINT_V2.md) |
| Modo narrativo vs replicación empírica, disclaimers | [MODE_NARRATIVE_VS_EMPIRICAL.md](MODE_NARRATIVE_VS_EMPIRICAL.md) |
| Alineación arXiv ↔ tema de misión | [ARXIV_TARGET_ALIGNMENT.md](ARXIV_TARGET_ALIGNMENT.md) |
| Baselines y métricas (plantilla de estudio) | [BASELINES_AND_METRICS_TEMPLATE.md](BASELINES_AND_METRICS_TEMPLATE.md) |
| Flujo de usuario extremo a extremo (CLI, bucles, Cursor) | [GUIA_FLUJO_COMPLETO.md](GUIA_FLUJO_COMPLETO.md) |
| Validar pieza por pieza (CLI, API, debug) | [GUIA_PRUEBAS_Y_DEBUG.md](GUIA_PRUEBAS_Y_DEBUG.md) |
| Escenarios E2E manuales (M1–M6), integración y Cockpit Playwright | [E2E_SCENARIOS.md](E2E_SCENARIOS.md) |
| Checklist operador (niveles 1–10, Notion, paralelo) | [PRUEBAS_NIVELES_5_10_NOTION.md](PRUEBAS_NIVELES_5_10_NOTION.md) |
| Run “real” sin mocks (SOTA, figuras, cuota API) | [FLUJO_REAL_SOTA_FIGURES.md](FLUJO_REAL_SOTA_FIGURES.md) |
| Qué archivo aparece en `outputs/` y quién lo escribe | [OUTPUTS_REFERENCE.md](OUTPUTS_REFERENCE.md) |
| Variables `.env` y flags de misión (Cursor reintentos, bucle experimento post-Cursor) | [VARIABLES_Y_FLAGS.md](VARIABLES_Y_FLAGS.md) |
| Hipervisor, tiers, `paper-parallel`, worktrees (guía larga) | [HIPERVISOR_Y_PARALELO.md](HIPERVISOR_Y_PARALELO.md) |
| Notion solo para triaje tier 3 | [NOTION_MCP_TRIAGE.md](NOTION_MCP_TRIAGE.md) |
| Cursor + Perplexity antes de un run largo | [PREFLIGHT_INTEGRACION.md](PREFLIGHT_INTEGRACION.md) |
| Contribuir (tests, `web/`, convenciones) | [DESARROLLO_Y_CONTRIBUCION.md](DESARROLLO_Y_CONTRIBUCION.md) |
| Cockpit en Vercel (API remota, CORS) | [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md) · [web/README.md](../web/README.md) |
| Arquitectura interna (módulos, API, seguridad) | [technical/00-indice.md](technical/00-indice.md) |
| Inventario completo: CLIs (`paper-*`), extras pip, env sueltos | [technical/07-inventario-cli-y-entorno.md](technical/07-inventario-cli-y-entorno.md) |
| Cerebro (Gemini): catálogo L1, análisis vs OpenClaw | [technical/brain-openclaw-gap.md](technical/brain-openclaw-gap.md), [paper_pipeline/brain/brain_capabilities.md](../paper_pipeline/brain/brain_capabilities.md) |
| Referencia HTTP (cockpit, ledger, triaje, publicación) | [technical/03-servidor-api.md](technical/03-servidor-api.md) |
| Contratos técnicos nuevos (`Safety`, `Objective`, `Memory`) | [technical/03-servidor-api.md](technical/03-servidor-api.md) |
| Evaluación determinista del agente (harness, sin Perplexity en CI) | [technical/agent-eval-spec.md](technical/agent-eval-spec.md) |
| Artefactos citables para un preprint **sobre el sistema** (tabla, límites, comandos) | [PREPRINT_ARTIFACTS.md](PREPRINT_ARTIFACTS.md) |
| Caso de uso P2 (informe + fixture + claims deterministas) | [examples/safety_usecase/report.md](../examples/safety_usecase/report.md) |
| Claims del preprint (B+C, límites, related work ancla) | [PREPRINT_CLAIM.md](PREPRINT_CLAIM.md) |
| Esqueleto Plan v2 (claim, abstract con corchetes, tabla sección→artefacto) | [PREPRINT_SKELETON.md](PREPRINT_SKELETON.md) |
| Borrador de manuscrito en inglés (alineado a artefactos actuales) | [preprint/PREPRINT_DRAFT.md](preprint/PREPRINT_DRAFT.md) |
| Figuras Mermaid (arquitectura, export PNG) | [assets/README.md](assets/README.md) |
| Paquete preprint (figuras generadas + snapshot appendix) | [preprint/README.md](preprint/README.md) |
| JSON `benchmark_bundle` (harness + ledger + traza; sin red) | `python -m paper_pipeline.reporting.benchmark_bundle` · [preprint/README.md](preprint/README.md) |
| Plan v3: reproducibilidad y tablas comparativas | [REPRODUCIBILITY_NOTES.md](REPRODUCIBILITY_NOTES.md) · [preprint/COMPARATIVE_TABLES.md](preprint/COMPARATIVE_TABLES.md) · [plan-v3-quantitative-reproducibility.md](superpowers/plans/plan-v3-quantitative-reproducibility.md) |
| Plan de trabajo: preprint **sobre paper-pipeline** (claim, artefactos, caso de uso safety) | [superpowers/plans/mio.md](superpowers/plans/mio.md) · [redirección del plan corto inicial](superpowers/plans/2026-03-31-preprint-artefactos-mision.md) |
| Estrategia Perplexity (perfiles, trazas de llamadas) | [technical/perplexity-strategy-spec.md](technical/perplexity-strategy-spec.md) |
| Árbol de metas (`goals.json`) | [technical/goals-spec.md](technical/goals-spec.md) |

## Comando de tests recomendado (CI local)

Por defecto se excluyen pruebas que llaman a **Perplexity** (`integration`), **Notion** (`notion_real`) y las E2E con navegador (`e2e`, `cockpit_e2e`) salvo que tengas `web/dist`, Playwright y tiempo de CI:

```bash
pytest -m "not integration and not notion_real and not e2e and not cockpit_e2e" -q
```

Solo humo Perplexity / Notion: `pytest -m integration` o `pytest -m notion_real`. E2E Cockpit: `pytest tests/test_cockpit_e2e.py -m cockpit_e2e` (ver [E2E_SCENARIOS.md](E2E_SCENARIOS.md)). Marcador `autonomy_integration` documentado en el mismo archivo.

## Otros

- Ejemplo de contenido para `cursor_turn.md`: [cursor_turn.example.md](cursor_turn.example.md)
