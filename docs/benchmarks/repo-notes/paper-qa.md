# paper-qa (Future-House)

## Patrón principal

RAG agentico sobre PDFs científicos con herramientas (`PaperSearch`, `GatherEvidence`, `GenerateAnswer`) y citas ancladas a pasajes.

## 3 ideas adoptables

1. Ingesta de PDF con metadatos DOI antes de generar texto.
2. Bucle gather-evidence → answer con trazabilidad por página.
3. Chequeo de retracciones / calidad de journal en metadatos.

## Archivos fuente

- `research-repos/paper-qa/src/paperqa/agents/tools.py`
- `research-repos/paper-qa/src/paperqa/docs.py`

## Mapeo paper-pipeline

- `paper_pipeline/rag/` + `literature/arxiv_fetch.py`
- `validation/claim_extractor.py` para grounding

## Riesgo / limitación

Dependencia LiteLLM/tantivy; coste de indexación local.

## Prioridad

P1
