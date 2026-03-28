# Documentación técnica (ingeniería) — paper-pipeline

Índice de documentos de arquitectura interna (no sustituye al README de usuario).

| Doc | Contenido |
|-----|-----------|
| [01-arquitectura.md](01-arquitectura.md) | Módulos, dependencias, flujo de datos |
| [02-orquestador.md](02-orquestador.md) | Fases del pipeline, `manifest.json`, reanudación |
| [03-servidor-api.md](03-servidor-api.md) | FastAPI, routers, SSE, validación de `mission_id` |
| [04-integraciones.md](04-integraciones.md) | Perplexity, Notion, Cursor CLI (reintentos headless), bucle experimento post-Cursor |
| [05-paralelo-triage.md](05-paralelo-triage.md) | Worktrees, `command_safety`, triage |
| [06-seguridad.md](06-seguridad.md) | Paths, tokens, comandos |
| [07-inventario-cli-y-entorno.md](07-inventario-cli-y-entorno.md) | **Inventario:** todos los `project.scripts`, extras pip, variables sueltas, mapa de módulos |
| [agent-eval-spec.md](agent-eval-spec.md) | Harness de evaluación determinista (`agent_eval`, escenarios JSON) |
| [perplexity-strategy-spec.md](perplexity-strategy-spec.md) | Perfiles Perplexity, `perplexity_call_record.jsonl` |
| [goals-spec.md](goals-spec.md) | Árbol `goals.json`, override de selección |
| [brain-openclaw-gap.md](brain-openclaw-gap.md) | Cerebro (Gemini): equivalencias y límites vs patrón OpenClaw |
| [brain-learnings-future.md](brain-learnings-future.md) | Diseño futuro (no implementado): lecciones tipo `.learnings/` con revisión humana |
| [EVALUATION_LAYERS.md](EVALUATION_LAYERS.md) | Calidad asistida vs claims vs revisión externa |
| [MVP_BENCHMARK.md](MVP_BENCHMARK.md) | Contrato mínimo `metrics.json` para benchmark ejecutable |
| [ROADMAP_MULTI_AGENT.md](ROADMAP_MULTI_AGENT.md) | Roadmap multi-agente iterativo (fuera del pipeline lineal) |

Archivos clave:

- Pipeline: [`paper_pipeline/pipeline/runner.py`](../../paper_pipeline/pipeline/runner.py)
- API: [`paper_pipeline/server/main.py`](../../paper_pipeline/server/main.py), [`paper_pipeline/server/routers/`](../../paper_pipeline/server/routers/)
- Cerebro L1: [`paper_pipeline/brain/brain_capabilities.md`](../../paper_pipeline/brain/brain_capabilities.md), [`paper_pipeline/brain/prompts.py`](../../paper_pipeline/brain/prompts.py)
- Eventos: [`paper_pipeline/events.py`](../../paper_pipeline/events.py)

Índice de toda la carpeta `docs/` (guías de usuario vs técnicas): [README.md](../README.md).
