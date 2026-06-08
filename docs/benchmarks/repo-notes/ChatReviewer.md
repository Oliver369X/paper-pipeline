# ChatReviewer

## Patrón principal

Revisión en dos etapas: elegir 2 secciones críticas → review estructurado con plantilla fija.

## 3 ideas adoptables

1. Stage 1 JSON con secciones foco (implementado en `quality_two_phase.py`).
2. Stage 2 con H2 Strengths/Weaknesses/Missing citations/Suggestions.
3. Separación generador vs revisor (Mistral quality con temperature baja).

## Archivos fuente

- `research-repos/ChatReviewer/chat_reviewer.py`

## Mapeo paper-pipeline

- `pipeline/quality_phase.py`
- `pipeline/quality_two_phase.py`

## Riesgo / limitación

Mismo proveedor Mistral para generar y revisar — no es revisor humano independiente.

## Prioridad

P0
