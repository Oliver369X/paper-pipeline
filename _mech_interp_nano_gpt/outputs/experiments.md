<!-- section=experiments generated=2026-03-26T19:31:48.390340+00:00 model=best -->

A continuación te propongo un **plan de experimento concreto** para estudiar **interpretabilidad mecanicista en modelos tipo nanoGPT pequeños, entrenables solo en CPU**, con foco en **circuitos indirectos, atención y hooks de activación** (línea Olsson/Nanda/Anthropic, sin GPU). El plan está pensado para caber en una **nota técnica reproducible** (arXiv / blog).

***

### 1) Baselines sugeridos

- **Baseline attention‑only minimalista (1–2 layers)**  
  - Transformer attention‑only (sin MLP) en estilo de [Adhikari et al. 2025], entrenado en una tarea IOI‑like sintética.[1](https://www.arxiv.org/abs/2510.25013)
  - Objetivo: entender cómo se configuran circuitos indirectos con muy pocos componentes.

- **Baseline GPT‑2 Small (IOI)**  
  - Modelo GPT‑2 Small resolviendo IOI mediante el conocido circuito de cabezas (≈26 heads) descrito en Wang et al..[2](https://arxiv.org/html/2407.11215v1)[3](https://www.neelnanda.io/mechanistic-interpretability/walkthrough-ioi)
  - Objetivo: comparar tamaño y complejidad del circuito en modelos grandes vs. muy pequeños.

- **Baseline nanoGPT sin interpretación estructurada**  
  - Un nanoGPT estándar entrenado en la misma tarea IOI‑like, pero sin usar hooks ni patching; solo se evalúa rendimiento (accuracy).  
  - Objetivo: mostrar que el uso de hooks y análisis de circuitos no degrada el rendimiento, pero permite exposición interna.

- **Baseline CPU‑only sin hooks**  
  - Misma arquitectura, pero sin guardar hooks ni analizar circuitos; solo se reporta accuracy y pérdida.  
  - Objetivo: medir el “precio” de almacenar y analizar hooks en términos de memoria y tiempo.

***

### 2) Métricas

#### 2.1) Métricas de rendimiento

- **Accuracy IOI‑like**  
  - Proporción de veces que el modelo predice el objeto indirecto correcto en el conjunto de validación.  
- **Perplexity / loss**  
  - Media de loss en el token objetivo en el dataset IOI‑like.

#### 2.2) Métricas de circuitos indirectos

- **Circuit size**  
  - Número de heads y capas en el subgrafo mínimo que, cuando se suprime, hace bajar el accuracy de forma significativa.  
- **Circuit depth**  
  - Máxima distancia en capas del camino desde entrada hasta último head relevante.  
- **Indirectness score (operacional)**  
  - Suma de:  
    - Número de heads en el camino,  
    - Número de capas atravesadas,  
    - Distancia posicional entre token relevante y último head (en tokens, no solo en capas).[4](https://arxiv.org/html/2602.03506v1)[5](https://arxiv.org/html/2407.02646v4)

#### 2.3) Métricas de hooks y coste computacional

- **Activation storage overhead**  
  - Tamaño total de archivos de hooks (bytes) vs. tamaño del modelo.  
- **Inference + hooking time**  
  - Tiempo medio por ejemplo en CPU (solo forward + guardar hooks).  
- **Memory footprint**  
  - pico de RAM durante inferencia + análisis de hooks.

***

### 3) Ablations

- **Arquitectura**  
  - Ablation:  
    - Atención‑only vs. atención + MLP.  
    - 1 capa vs. 2 capas vs. 4 capas.  
  - Pregunta: ¿cómo cambia el tamaño y la estructura del circuito indirecto?

- **Mecanismo de interpretación**  
  - Ablation:  
    - Con vs. sin hooks y patching.  
    - Con vs. sin análisis de circuitos (solo reporta accuracy).  
  - Pregunta: ¿el análisis de circuitos afecta el rendimiento, o solo la explicabilidad?

- **Dataset IOI‑like**  
  - Ablation:  
    - Entrenamiento en datos sintéticos IOI vs. texto natural más complejo.  
  - Pregunta: ¿cómo se degradan los circuitos “limpios” en modelos que ven más diversidad?

- **Indirectness vs. robustness**  
  - Ablation:  
    - Quitar un head “indirecto” (IOI) vs. un head “directo” (copia).  
  - Pregunta: ¿qué tipo de head es más crítico para la tarea?

***

### 4) Consideraciones de presupuesto computacional

- **Modelo pequeño**  
  - 전체 크기: 12M–50M parámetros, máximo 4 capas, 2–8 heads, contextos cortos (≈16–64 tokens).[5](https://arxiv.org/html/2407.02646v4)[6](https://github.com/karpathy/nanogpt)
  - Objetivo: entrenamiento y análisis en CPU en menos de 24h en una máquina modesta (8–16 GB RAM).

- **Hooks y almacenamiento**  
  - Guardar hooks solo en **evaluación** (no en entrenamiento completo), lo que reduce el coste de escritura.  
  - Usar formatos eficientes (NumPy `.npz`, HDF5) para guardar solo activaciones relevantes (no gradientes).[7](https://coairesearch.org/notes/democratizing-mechinterp/)[5](https://arxiv.org/html/2407.02646v4)

- **Patching**  
  - Ejecutar patching solo en un **subconjunto pequeño pero representativo** del dataset (por ejemplo, 100–500 ejemplos) para mantener el análisis manejable en CPU.

- **Código modular**  
  - Separar módulos claros:  
    - `train_cpu.py` (entrenamiento en CPU),  
    - `hooks.py` (registro de activaciones),  
    - `patching.py` (activation patching),  
    - `circuit_analysis.py` (pruning y métricas de circuitos).[8](https://www.lesswrong.com/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)[9](https://aisst.ai/tech-papers)

***

### 5) Tabla de resultados (propuesta en Markdown)

Abajo va un ejemplo de tabla que puedes usar en tu nota técnica para presentar resultados de forma clara y comparativa.

| Modelo / Configuración | Accuracy IOI (%) | Circuit size (heads) | Circuit depth (capas) | Indirectness score | Storage overhead (MB) | Hooking time (s/instancia) |
|------------------------|-------------------|------------------------|------------------------|---------------------|------------------------|-----------------------------|
| Attention‑only (1 capa) | 85.2 | 2 | 1 | 3.5 | 45 | 0.12 |
| Attention‑only (2 capas) | 91.1 | 3 | 2 | 5.2 | 65 | 0.16 |
| nanoGPT (1 capa, MLP) | 88.7 | 4 | 2 | 6.1 | 105 | 0.18 |
| nanoGPT (2 capas, MLP) | 94.3 | 5 | 3 | 7.8 | 140 | 0.22 |
| nanoGPT (4 capas, MLP) | 96.1 | 7 | 4 | 8.9 | 220 | 0.30 |
| GPT‑2 Small (IOI) [ref] | 98.5 | 26 | 12 | 18.4 | 2000 | 0.65 |
| nanoGPT (sin hooks) | 94.2 | N/A | N/A | N/A | 120 | 0.15 |

**Notas**:  
- `Circuit size` = número de heads en el circuito mínimo identificado.  
- `Indirectness score` = combinación de tamaño, profundidad y distancia posicional.  
- `Storage overhead` = tamaño total de archivos de hooks vs. tamaño del modelo.  
- `Hooking time` = tiempo medio por ejemplo en CPU (solo inferencia + hooks).[1](https://www.arxiv.org/abs/2510.25013)[4](https://arxiv.org/html/2602.03506v1)[5](https://arxiv.org/html/2407.02646v4)

***

¿Quieres que en el siguiente paso te ayude a **escribir el esqueleto de la nota técnica** (estructura de secciones, ejemplos de figures, y checklist de artefactos de código/datos)?
