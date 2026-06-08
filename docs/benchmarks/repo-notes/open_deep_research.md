# open_deep_research

## Patrón principal

LangGraph: clarificación → brief → investigación concurrente → compresión de notas → informe final con estado tipado.

## 3 ideas adoptables

1. Supervisor + sub-investigadores con presupuesto (`research_agent_phase.py`).
2. Compresión intermedia de notas antes del draft (futuro).
3. Harness Deep Research Bench lite (`benchmarks/deep_research_lite.py`).

## Archivos fuente

- `research-repos/open_deep_research/src/open_deep_research/deep_researcher.py`
- `research-repos/open_deep_research/src/open_deep_research/state.py`

## Mapeo paper-pipeline

- `pipeline/research_agent_phase.py`
- `paper_pipeline/benchmarks/deep_research_lite.py`

## Riesgo / limitación

LangGraph como dependencia pesada; V1 usa trace JSONL sin grafo completo.

## Prioridad

P1
