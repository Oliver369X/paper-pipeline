# ChatPaper

## Patrón principal

Pipeline paper-centric: parseo PDF, resumen por paper, crawl arXiv, auto-survey con FAISS.

## 3 ideas adoptables

1. Ingesta arXiv por ID en `literature/arxiv_fetch.py`.
2. Parser de secciones PDF (roadmap P2).
3. Auto-survey keywords → embeddings (roadmap).

## Archivos fuente

- `research-repos/ChatPaper/chat_arxiv.py`
- `research-repos/ChatPaper/auto_survey/main.py`

## Mapeo paper-pipeline

- `paper_pipeline/literature/arxiv_fetch.py`

## Riesgo / limitación

PyMuPDF/FAISS añaden peso; Mistral no sustituye PDF parsing.

## Prioridad

P1
