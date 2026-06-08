# local-deep-research

## Patrón principal

20+ estrategias de búsqueda plugables, biblioteca indexada, CitationHandler thread-safe, benchmarks SimpleQA.

## 3 ideas adoptables

1. Índice global de citas en ensamblado (`citation_index.py`).
2. Registry de estrategias por modo (alineado a `perplexity-strategy-spec.md`).
3. Almacenamiento cifrado de biblioteca personal (roadmap).

## Archivos fuente

- `research-repos/local-deep-research/src/local_deep_research/advanced_search_system/strategies/`
- Citation handler modules under same tree

## Mapeo paper-pipeline

- `pipeline/citation_index.py`
- `pipeline/assembly_phase.py`

## Riesgo / limitación

Stack LangGraph+FAISS+SQLCipher es pesado para MVP.

## Prioridad

P0
