# Modo narrativo vs replicación empírica

## Modo narrativo (comportamiento por defecto del pipeline)

- **Qué hace:** genera secciones en Markdown vía Perplexity según `mission.md`, ensambla `draft_paper.md`, opcionalmente `quality_gaps.md` (revisión asistida por el mismo tipo de modelo).
- **Qué no demuestra:** experimentos ejecutados, números reproducibles contra un paper objetivo, ni equivalencia con un «agente autónomo» en sentido de ICML/NeurIPS.
- **Uso honesto:** borrador estructurado, lluvia de ideas, checklist metodológica — **no** «replicación científica» sin pasos adicionales.

## Modo replicación empírica (no viene listo en una sola pasada)

Requiere al menos:

1. **Pregunta alineada** con el paper citado (ver [ARXIV_TARGET_ALIGNMENT.md](ARXIV_TARGET_ALIGNMENT.md)).
2. **Código y datos** ejecutados fuera del texto (p. ej. `outputs/code/`, CI, sandbox, Colab) con métricas escritas en disco.
3. **Evaluación externa o humana** para claims cuantitativos (el `quality_check` interno es revisión asistida, no verdad empírica).

Ver también [technical/MVP_BENCHMARK.md](technical/MVP_BENCHMARK.md) y [BASELINES_AND_METRICS_TEMPLATE.md](BASELINES_AND_METRICS_TEMPLATE.md).
