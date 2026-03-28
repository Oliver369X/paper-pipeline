<!-- section=sota generated=2026-03-27T20:39:13.976904+00:00 model=best -->

The current state of the art for **análisis de la curvatura de la pérdida en la transición memorización–razonamiento** gira en torno a descomposiciones de la matriz de Fisher (o su aproximación K‑FAC) para separar direcciones “memorísticas” (baja curvatura agregada) de direcciones “generalistas/razonadoras” (curvatura moderada pero consistente) en modelos transformer.[1](https://arxiv.org/abs/2510.24256)[2](https://proceedings.mlr.press/v235/garg24a.html)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### 1. Idea central y paradigma actual

La idea central es que **la curvatura local del paisaje de pérdida** (en forma de eigenvalores de la matriz de Fisher o Hessian‑aproximación) puede servir como proxy para distinguir memorización de razonamiento:

- **Memorización puntual**: puntos con etiquetas memorizadas suelen tener regiones muy curvadas localmente, pero las direcciones de curvatura son idiosincráticas y cambian de ejemplo a ejemplo.[2](https://proceedings.mlr.press/v235/garg24a.html)[4](https://ar5iv.labs.arxiv.org/html/2307.05831)
- **Generalización/razonamiento**: mecanismos compartidos (attención, composición lógica, etc.) generan direcciones de **curvatura moderada pero estable** a través de muchos ejemplos; al promediar sobre la distribución, estas direcciones aparecen con mayor curvatura que las asociadas a memorización bruta.[5](https://arxiv.org/html/2510.24256v1)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

El trabajo más reciente que cristaliza este “spectrum” es:  
- **From Memorization to Reasoning in the Spectrum of Loss Curvature** (octubre–noviembre 2025).[6](https://huggingface.co/papers/2510.24256)[1](https://arxiv.org/abs/2510.24256)[5](https://arxiv.org/html/2510.24256v1)

***

### 2. Paradigma y métricas estándar

#### Paradigmas de análisis

- **K‑FAC / Fisher‑based curvature**: se estima la matriz de Fisher aproximada via K‑FAC para capas MLP/lineales y se descomponen los bloques peso $$W$$ en direcciones ordenadas por curvatura.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)[5](https://arxiv.org/html/2510.24256v1)
- **Weight editing basado en curvatura**: se eliminan componentes de baja curvatura y se miden caídas de rendimiento en tareas conectadas a memorización vs. razonamiento.[7](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

#### Métricas típicas reportadas

- **Curvature‑based “memorization score”**:  
  Para cada ejemplo o para subconjuntos, se usa el eigenvalor promedio o la norma de la dirección de curvatura asociada a esa muestra.[4](https://ar5iv.labs.arxiv.org/html/2307.05831)[2](https://proceedings.mlr.press/v235/garg24a.html)
- **Memorization suppression**:  
  - Exactitud en “out‑of‑distribution” memorized quotes (e.g., 16.1% strict accuracy vs 60.0% en BalancedSubnet, con mejor perplexity en OLMo‑2 7B).[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Generalization / robustness**:  
  - Perplexity en test, accuracy en validación (en ViTs se reporta mejora de 67.0% → 71.7% tras edición por curvatura).[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Task sensitivity**:  
  - Diferencia de performance en tareas de **fact retrieval**, **arithmetic** vs **logical reasoning**; por ejemplo, caídas sustanciales en fact/arithmetic pero robustez o mejora en razonamiento no numérico.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### 3. Benchmark datasets y tareas típicas

Los trabajos recientes se apoyan en varios tipos de benchmarks para separar memorización de razonamiento:

- **LMs / LLMs (OLMo‑2 7B, otros transformers)**:  
  - **Memorized historical quotes**: corpus de citas históricas inducidas a memorización para evaluar supresión de memorización.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
  - **Fact‑retrieval closeds‑book**: tareas como MMLU‑style, True/False, o versiones de fact‑retrieval con y sin contexto abierto.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - **Arithmetic y razonamiento lógico**: tareas de aritmética simbólica y razonamiento lógico (no‑numérico) en el spectrum memorización–razonamiento.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

- **Vision Transformers (ViTs)**:  
  - **Imagenet‑style classification**: se modifica una fracción de etiquetas con “noise” para estudiar memorización de etiquetas corruptas vs. generalización.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - **Memorization suppression**: se mide cuánto el modelo “recuerda” etiquetas corruptas antes y después de la edición de baja‑curvatura.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

- **Analyses de curvatura por ejemplo**:  
  - **Corrupted‑label datasets** (por ejemplo, CIFAR‑10/100 con etiquetas aleatorias en una fracción): se calcula la curvatura promedio por ejemplo y se separan datos corruptos (altas curvaturas) de limpios.[2](https://proceedings.mlr.press/v235/garg24a.html)[4](https://ar5iv.labs.arxiv.org/html/2307.05831)

***

### 4. Arquitecturas y parámetros típicos

- **Modelos estudiados**:  
  - **Transformers de lenguaje**: OLMo‑2 7B, otros LLMs; se usan capas MLP para K‑FAC y análisis de curvatura por peso.[5](https://arxiv.org/html/2510.24256v1)[6](https://huggingface.co/papers/2510.24256)[1](https://arxiv.org/abs/2510.24256)
  - **Vision Transformers (ViTs)**: ViTs entrenados en ImageNet‑style, con capas de MLP por patch.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

- **Paradigma de descomposición**:  
  - Para un peso $$W \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$$, se aproxima el bloque de Fisher como $$F_W \approx G \otimes A$$, donde  
    - $$G = \mathbb{E} [ g g^\top ]$$ (covarianza de gradients de salida),  
    - $$A = \mathbb{E} [ a a^\top ]$$ (covarianza de activations de entrada).[5](https://arxiv.org/html/2510.24256v1)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - Los eigenvalores curvatura se obtienen como productos $$\lambda_i \mu_j$$, y las direcciones se ordenan de **alta a baja curvatura**.[5](https://arxiv.org/html/2510.24256v1)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

- **Weight editing por curvatura**:  
  - Se seleccionan pares $$(i,j)$$ con curvatura acumulada hasta una fracción $$\rho$$ (e.g., 80–90%) y se reconstruyen los pesos usando solo esas direcciones.  
  - Componentes de baja curvatura (asociados a memorización) se anulan; se reporta baja en memorización con menor costo en razonamiento.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

***

### 5. Rangos y resultados representativos

- **Memorization suppression**:  
  - En OLMo‑2 7B, edición K‑FAC reduce **strict memorization accuracy** de quotes a ~16.1% frente a ~60.0% en BalancedSubnet, manteniendo perplexity más baja.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Generalization / robustness**:  
  - En ViTs con etiquetas ruidosas, se observa mejora de **67.0% → 71.7%** en validación y mejor recuperación de etiquetas verdaderas tras edición por curvatura.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Espectro memorización–razonamiento**:  
  - Tareas de **arithmetic** y **closed‑book fact retrieval** muestran alta sensibilidad a remoción de direcciones de baja curvatura.  
  - Tareas de **logical reasoning** y **open‑book fact retrieval** son robustas o incluso mejoran ligeramente.[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### 6. Fuentes clave (con URLs)

- **“From Memorization to Reasoning in the Spectrum of Loss Curvature” (2025)** – trabajo central del estado del arte:  
  - arXiv: https://arxiv.org/abs/2510.24256[6](https://huggingface.co/papers/2510.24256)[5](https://arxiv.org/html/2510.24256v1)[1](https://arxiv.org/abs/2510.24256)
- **Goodfire AI blog explicativo**:  
  - https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature[7](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **Artículo anterior sobre “Memorization Through the Lens of Curvature of Loss Function” (Garg et al.)**:  
  - https://arxiv.org/html/2307.05831[4](https://ar5iv.labs.arxiv.org/html/2307.05831)
- **Resumen/comentario técnico del paper de 2025**:  
  - https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

Si quieres, puedo profundizar en cómo traducir este marco de curvatura a métricas explícitas para tu propio experimentation (por ejemplo, definir un “score de curvatura por ejemplo” en un LLM pequeño entrenado en tu propio corpus). ¿Quieres que lo enfoquemos en un dataset específico (por ejemplo, un corpus de exámenes tipo MMLU o un dataset local boliviano)?
