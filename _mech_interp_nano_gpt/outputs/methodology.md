<!-- section=methodology generated=2026-03-26T19:31:17.251792+00:00 model=best -->

A continuación te propongo un **método concreto y reproducible** para estudiar **interpretabilidad mecanicista en modelos tipo nanoGPT pequeños, entrenables solo en CPU**, con foco en **circuitos indirectos, atención y hooks de activación** (línea Olsson/Nanda/Anthropic, sin GPU), pensado para una **nota técnica** (arXiv / blog).  

***

### 1) Problema a formular

**Objetivo principal**:  
Demostrar que, en un transformer pequeño tipo nanoGPT entrenado solo en CPU, es posible:  
- identificar de forma **clara y reproducible** **circuitos indirectos** (por ejemplo, IOI‑like) que resuelven tareas sintáctico‑semánticas sencillas,  
- caracterizar cómo estos circuitos se distribuyen entre **atención y hooks de activación** en capas tempranas/intermedias,  
- y proporcionar un **pipeline CPU‑only** que otro investigador pueda reproducir paso a paso.

**Formulación concreta (ejemplo core)**:  
- “¿Puede un modelo nanoGPT de tamaño pequeño (≈1–4 capas, objetivo razonablemente bajo) aprender un circuito IOI‑like, y se puede aislar este circuito mediante **hooks de activación y patching** en un flujo completamente CPU‑compatible?”[1](https://arxiv.org/html/2407.11215v1)[2](https://www.arxiv.org/abs/2510.25013)[3](https://www.lesswrong.com/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)

***

### 2) Baselines contra las que comparar

Conviene compararse con **versiones “conocidas”** de la misma tarea, para que tu nota tenga anclaje:

- **Baseline simbólico minimalista (1–2 capas, atención‑only)**  
  - Modelo: pequeño transformer **atención‑only** (sin MLP) en el estilo de Adhikari et al., entrenado en una versión simplificada de IOI.[2](https://www.arxiv.org/abs/2510.25013)[4](https://arxiv.org/pdf/2510.25013.pdf)
  - Métrica: circuito minimal (1–2 cabezas) identificado mediante análisis de residuos y patching.  
  - Tu contribución: comparar **tamaño del modelo y tipo de arquitectura** (MLP vs. atención‑only) en circuitos indirectos.

- **Baseline IOI‑GPT2 Small (GPT‑2 Small + TransformerLens)**  
  - Modelo: GPT‑2 Small resuelviendo IOI, con el circuito de 26 cabezas descrito por Wang et al..[5](https://www.neelnanda.io/mechanistic-interpretability/walkthrough-ioi)[1](https://arxiv.org/html/2407.11215v1)
  - Tu contribución:  
    - No repetir el circuito completo, sino usarlo como **analogía** para plantear las mismas preguntas (cómo se ve en un modelo pequeño) y  
    - como referencia para elegir métricas de “indirectness” y fidelidad funcional.

- **Baseline sin interpretación estructurada (solo rendimiento en IOI‑like)**  
  - Modelo nanoGPT estándar (sin hooks ni patching) entrenado en la misma tarea, pero con evaluación solo en **accuracy** y **logits**.  
  - Tu contribución: mostrar que **añadir mecanismos de interpretación** (hooks, patching, circuitos) mejora la **explicabilidad** sin sacrificar capacidad, y permite entender cómo se toma la decisión.

***

### 3) Diseño metodológico (método paso a paso)

#### 3.1) Entorno y modelo

- **Modelo**:  
  - Un nanoGPT muy pequeño (≈1–4 capas, 2–8 heads, vocab pequeño, contexto corto) basado en el repositorio de Karpathy pero adaptado para CPU:  
    - `device=cpu`, `torch.compile=False` u otra opción que evite el uso de GPU.[6](https://github.com/karpathy/nanogpt)
  - Alternativa: un **transformer attention‑only minimalista** (1–2 capas) en el estilo de Adhikari et al..[4](https://arxiv.org/pdf/2510.25013.pdf)[2](https://www.arxiv.org/abs/2510.25013)

- **Tarea**:  
  - Un **IOI‑like** de lenguaje sintético:  
    - Ejemplo: “After John and Mary went to the shop, John gave a drink to …” → debe completar con “Mary”.[1](https://arxiv.org/html/2407.11215v1)[5](https://www.neelnanda.io/mechanistic-interpretability/walkthrough-ioi)
  - Dataset:  
    - Plantillas generadas a partir de listas de nombres, lugares, objetos, siguiendo el esquema de Redwood/Anthropic.[1](https://arxiv.org/html/2407.11215v1)
    - Longitud de contexto corta; entrenamiento limitado al CPU para garantizar que el modelo sea pequeño y reproducible.

#### 3.2) Entrenamiento CPU‑only

- **Entrenar el modelo** en CPU usando:  
  - nanoGPT o un fork ligero (por ejemplo, `build‑nanogpt` o una versión minimal de Karpathy).[7](https://github.com/karpathy/build-nanogpt/blob/master/README.md)[6](https://github.com/karpathy/nanogpt)
  - Enfocarse en un **tamaño pequeño** (por ejemplo, 12M–50M params) para que el experimento sea reproducible en máquinas modestas.[8](https://arxiv.org/html/2407.02646v4)

- **Artifacts generados**:  
  - Checkpoints versionados,  
  - Logs de pérdida y accuracy en IOI‑like,  
  - Dataset de entrenamiento/eval procedimentalmente generable.

#### 3.3) Hooks de activación y análisis CPU‑friendly

- **Hooking**:  
  - Usar un **lenguaje de hooks minimalista** (inspirado en `TransformerLens` o `nnterp`) que registre, para cada paso, los valores de:  
    - `resid_pre`, `resid_post`, `attn.hook_v`, `attn.hook_z`, `mlp.hook_post` (si usa MLP).[3](https://www.lesswrong.com/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)[9](https://aisst.ai/tech-papers)
  - Guardar todas las activaciones de evaluación en **arrays NumPy** o archivos `.h5` / `.npz` (no GPU‑only, solo CPU‑compatible).[10](https://coairesearch.org/notes/democratizing-mechinterp/)[8](https://arxiv.org/html/2407.02646v4)

- **Métricas de análisis**:  
  - **Activación media por capa/cabeza** en el token de predicción,  
  - **Spectral analysis** o **SVD reducida** en el residual stream para detectar direcciones de información relevantes.[11](https://arxiv.org/html/2602.03506v1)[8](https://arxiv.org/html/2407.02646v4)

#### 3.4) Descubrimiento de circuitos indirectos (patching + pruning)

- **Patching**:  
  - Implementar **activation patching** sencillo:  
    - Correr el modelo en un ejemplo “correcto” y uno “corrupto” (por ejemplo, cambiando nombres),  
    - Parchear el **residual stream** en cierta capa (`post‑i` o `pre‑j`) y medir el impacto en el logit final.[3](https://www.lesswrong.com/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)[11](https://arxiv.org/html/2602.03506v1)
  - Mapear qué combinaciones de capas y cabezas tienen mayor “efecto indirecto” en la predicción.

- **Circuit discovery**:  
  - Usar una versión simplificada de **ACDC** o **iterative patching** para aislar un subgrafo mínimo:  
    - Mantener un conjunto de “edges” (cabezas, capas) y luego retirarlos uno a uno mientras se mide el descenso en accuracy.[12](https://neurips.cc/virtual/2023/poster/72666)[11](https://arxiv.org/html/2602.03506v1)
  - Definir un **criterio mínimo** de “minimality” (por ejemplo, que retirar cualquier componente disminuya el accuracy en más de un umbral pequeño).

- **Taxonomía de circuitos**:  
  - Clasificar los circuitos encontrados en:  
    - Direct heads (copia directa),  
    - Indirect heads (inducción‑like),  
    - Combinaciones de atención + MLP que integran información de múltiples pasos.[2](https://www.arxiv.org/abs/2510.25013)[8](https://arxiv.org/html/2407.02646v4)

#### 3.5) Métrica de “indirectness” operable en CPU

- Proponer una métrica simple de **indirectness de circuito**:  
  - Número de cabezas involucradas en el camino,  
  - Profundidad en capas (capa de inicio → capa de último head),  
  - Dependencia de posiciones anteriores no adyacentes (por ejemplo, `pos_n` depende de `pos_n‑k` con `k>1`).[11](https://arxiv.org/html/2602.03506v1)[8](https://arxiv.org/html/2407.02646v4)
- Validar que, cuando se borra un circuito “indirecto”, la predicción falla, pero el modelo aún puede resolver tareas más simples (por ejemplo, copia directa).

***

### 4) Qué cuenta como resultado mínimo viable (minimal viable result)

Para que tu nota técnica sea aceptable como **reproducible** (arXiv / blog), considera suficiente:

1. **Demostrar que un modelo nanoGPT pequeño resuelve IOI‑like**  
   - Mostrar que el modelo alcanza **alta accuracy** en la tarea IOI‑like, comparable a modelos más grandes en el mismo tipo de tarea.[2](https://www.arxiv.org/abs/2510.25013)[1](https://arxiv.org/html/2407.11215v1)

2. **Identificar al menos un circuito indirecto claro**  
   - Encontrar un **subgrafo mínimo de attention heads** (por ejemplo, 1–3 heads en 1–2 capas) cuyo patching o supresión hace que el modelo deje de resolver IOI,  
   - Y describir este subgrafo en términos de atención (qué token copia, qué token suprime, cómo se suma en el residual stream).[11](https://arxiv.org/html/2602.03506v1)[2](https://www.arxiv.org/abs/2510.25013)

3. **Proporcionar un pipeline CPU‑only reproducible**  
   - Publicar un repositorio con:  
     - código de entrenamiento en CPU,  
     - código de generación de dataset IOI‑like,  
     - código de hooks y patching,  
     - ejemplos de visualización de circuitos y análisis de activaciones.[10](https://coairesearch.org/notes/democratizing-mechinterp/)[6](https://github.com/karpathy/nanogpt)
   - Incluir instrucciones claras para que otro investigador pueda reproducir el experimento en una máquina sin GPU.

4. **Mostrar al menos una comparación estructurada**  
   - Comparar tu modelo nanoGPT con:  
     - el baseline IOI‑GPT2 Small en términos de **tamaño de circuito y número de cabezas**,  
     - o con un modelo pequeño atención‑only en términos de **complejidad del circuito**.[13](https://www.alphaxiv.org/overview/2511.13653v1)[1](https://arxiv.org/html/2407.11215v1)[2](https://www.arxiv.org/abs/2510.25013)

Con estos cuatro elementos estarías presentando un resultado **mínimo pero sólido**: un estudio de interpretabilidad mecanicista en un modelo tipo nanoGPT pequeño, entrenable solo en CPU, con foco en circuitos indirectos, atención y hooks, y claramente reproducible.

***

¿Quieres que en el siguiente paso te ayude a **escribir el esqueleto de la nota técnica** (estructura de secciones, ejemplos de figures, y checklist de artefactos de código/datos)?
