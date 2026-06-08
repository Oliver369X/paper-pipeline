# OpenScholar

## Patrón principal

RAG sobre ~45M papers open-access; supera PaperQA2/Perplexity Pro en evaluaciones Nature 2025.

## 3 ideas adoptables

1. Retrieval denso + rerank antes de síntesis (extender `paper_pipeline/rag/`).
2. Respuestas preferidas vs GPT-4o-only como baseline documentado.
3. Semantic Scholar como backend de retrieval.

## Archivos fuente

- `research-repos/OpenScholar/src/open_scholar/` (layout may vary)
- `research-repos/OpenScholar/README.md`

## Mapeo paper-pipeline

- `paper_pipeline/rag/service.py`
- `literature/arxiv_fetch.py`

## Riesgo / limitación

Modelos/checkpoints grandes; no trivial en laptop.

## Prioridad

P2
