# Claims del preprint — claridad (P-1)

Documento interno para alinear autores y revisores: **qué defiende el manuscrito** y **qué no**. Complementa [PREPRINT_ARTIFACTS.md](PREPRINT_ARTIFACTS.md) (artefactos técnicos) y [superpowers/plans/mio.md](superpowers/plans/mio.md) (plan vivo).

---

## Afirmaciones en lenguaje de paper (tres niveles)

### 1. Sistemas (Claim B)

**Texto tipo contribución técnica:**  
Proponemos una arquitectura open source para pipelines de investigación asistidos por LLM que combina un ledger de ejecución, triaje de resultados, un harness de evaluación determinista de gobernanza (`agent_eval`), y controles explícitos de coste y secretos. El diseño está documentado, versionado en pruebas y reproducible sin APIs de modelo en la parte del harness.

**Evidencia en repo:** [architecture/status-matrix.md](architecture/status-matrix.md), baseline en [examples/baselines/agent_eval_baseline.json](../examples/baselines/agent_eval_baseline.json), tests `test_agent_eval_*`.

### 2. Aplicación (Claim C)

**Texto tipo motivación:**  
Ese patrón es especialmente pertinente cuando la reproducibilidad y la auditabilidad del *proceso* de investigación importan tanto como el resultado — por ejemplo en trabajo sobre memorización, interpretabilidad mecánica y políticas de edición de modelos, donde los papers a menudo no se replican de forma comparable entre equipos.

**Evidencia en repo:** caso anclado en [examples/safety_usecase/report.md](../examples/safety_usecase/report.md) (arXiv:2510.24256 como tema; límites explícitos sobre qué está en CI).

### 3. Posicionamiento (contexto / related work)

**Texto tipo gap:**  
La literatura reciente subraya que la replicación automatizada de papers ML y la evaluación comparable entre estudios siguen siendo problemas abiertos; las herramientas genéricas de orquestación no ofrecen por sí mismas contratos de auditabilidad ni regresión sobre políticas de publicación.

**Referencias ancla (a citar en el borrador del paper):**

| Trabajo | arXiv | Rol en el argumento |
|---------|-------|---------------------|
| PaperBench (OpenAI, 2025) | 2504.01848 | Gap de replicación automatizada a escala |
| MIB (Mechanistic Interpretability Benchmark, 2025) | 2504.13151 | Necesidad de infraestructura de evaluación comparable |
| Merullo et al. — memorización vs razonamiento (curvatura) | 2510.24256 | Paper de aplicación / caso de uso P2 |

---

## Borrador de abstract (un párrafo, inglés académico neutro)

> We present **paper-pipeline**, an open-source system for LLM-assisted research drafting that makes execution traces, publication gates, and governance checks first-class artifacts. The stack combines a deterministic agent-evaluation harness (safety and goal-selection oracles), triage over mission metrics, and explicit handling of credentials and API budgets. We motivate the design through AI-safety-adjacent research settings—where auditability and reproducibility of the research process are first-order requirements—and provide a minimal, fully documented use case around memorization-focused work (arXiv:2510.24256), separating what is regression-tested in CI from what still requires external compute or human review. We do not claim end-to-end replication of third-party experiments or user-study gains in workflow speed.

(Ajustar tono a la venue; el párrafo es plantilla, no versión final de envío.)

---

## Lo que el paper **no** afirma (tan importante como lo que sí)

1. **No** demuestra una ganancia medida de tiempo o calidad frente a un baseline humano (Claim A queda fuera del alcance actual).
2. **No** prueba generalización estadística a “todos los papers de safety”: el caso P2 es **un** ancla, documentada con límites.
3. **No** sustituye revisión por pares, validación estadística de claims cuantitativos en borradores LLM, ni ejecución GPU de réplicas del paper ancla dentro del repositorio.
4. **No** afirma que el harness `agent_eval` cubre todos los fallos posibles en producción: los escenarios son **sintéticos** y versionados.

---

## Preguntas de un revisor hostil — respuestas honestas

**P: “¿Por qué usar esto en lugar de LangChain + scripts?”**  
R: Porque el objetivo de diseño es explícito: trazas en disco, regresión sobre políticas de publicación y harness determinista sin coste de API. Los frameworks genéricos no prometen ese contrato; no compiten en features de chat.

**P: “Un solo caso de uso no demuestra que la arquitectura escala.”**  
R: Correcto. El manuscrito debe afirmar **reutilización del patrón** y **evidencia de aplicabilidad** en un escenario bien acotado, no validez estadística sobre N laboratorios.

**P: “Los números del borrador Perplexity pueden ser alucinaciones.”**  
R: Sí — por eso el sistema separa modo narrativo de evidencia empírica, checklist de claims y advertencias en [MODE_NARRATIVE_VS_EMPIRICAL.md](MODE_NARRATIVE_VS_EMPIRICAL.md). El paper debe decirlo sin ambigüedad.

---

## Criterio de hecho

Cualquier coautor puede leer este archivo y redactar Introducción + Contribuciones sin contradecir los artefactos en [PREPRINT_ARTIFACTS.md](PREPRINT_ARTIFACTS.md).
