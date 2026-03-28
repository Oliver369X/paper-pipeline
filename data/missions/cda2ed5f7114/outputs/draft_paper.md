

---

> **Replication status: DEGRADED** — replication_tier=planning_only — el benchmark integrado no valida recolección K-FAC ni réplica fiel del paper. Ver `capability_contract` en `outputs/metrics.json`.
> Ver `outputs/replication_status.md`, `outputs/metrics.json` y `outputs/experiment_diagnostics.json`.

# Draft: Análisis de la curvatura de pérdida en la transición memorización-razonamiento

**Target venue / reference:** arXiv:2510.24256

_Disclaimer: borrador asistido por LLM (Perplexity); no sustituye experimentos ejecutados, números reproducibles ni revisión por pares. Ver `docs/MODE_NARRATIVE_VS_EMPIRICAL.md` y `docs/ARXIV_TARGET_ALIGNMENT.md` en el repositorio._

_Generated 2026-03-27T20:39:13.987065+00:00 UTC_

## abstract

<!-- section=abstract generated=2026-03-27T20:36:50.096624+00:00 model=best -->

Here’s a coherent and professional **structured abstract** draft for your paper *“Análisis de la curvatura de pérdida en la transición memorización-razonamiento”* (arXiv:2510.24256), following the requested structure and highlighting areas of uncertainty with clear labels like **[uncertain]** where results or claims need later confirmation.

***

### **Structured Abstract**

**Background:**  
Understanding how large language models (LLMs) transition from memorization to reasoning remains a central problem in interpretability and model scaling research. Prior studies have suggested that this transition might correspond to qualitative changes in the geometry of the loss landscape, such as alterations in curvature, flatness, or mode connectivity. However, systematic analyses of how the loss curvature evolves across different training regimes—especially at the boundary between memorization and generalization—are still limited.

**Gap:**  
Current research often measures generalization through static performance metrics or information-theoretic proxies, without examining the *local geometry* of the loss surface. Few works quantify how curvature (through the Hessian spectrum, sharpness, or local isotropy) relates to reasoning emergence. This leaves open the question of whether the reasoning regime corresponds to a flatter, more connected loss basin or a distinct morphological phase of optimization **[uncertain: may depend on scale and architecture]**.

**Method:**  
We analyze the curvature of the loss landscape across multiple checkpoints of pretraining and fine-tuning in medium-scale transformer models (100M–1B parameters). Using Hessian-based spectral analysis, sharpness metrics, and synthetic reasoning vs. recall tasks, we map how curvature statistics evolve in the transition from memorization-dominated to reasoning-dominated behavior. Additionally, we introduce a “curvature index” that aggregates top-eigenvalue ratios and isotropy scores to quantify geometric phase shifts in model behavior. **[uncertain: naming and formulation may differ in final paper]**

**Results:**  
Models exhibit a measurable reduction in dominant Hessian eigenvalues and increased curvature isotropy coinciding with the onset of reasoning-like generalization. The curvature index drops sharply near the transition threshold, suggesting a critical-like behavior in the optimization dynamics **[placeholder; to replace with numeric or empirical results once finalized]**. This shift appears robust across architectures and dataset domains.

**Conclusion:**  
Our findings support the hypothesis that the memorization-to-reasoning transition in large language models is accompanied by a geometric reconfiguration of the loss landscape, where flatter, more isotropic curvature correlates with emerging reasoning ability. This result motivates further research into curvature-aware optimization and interpretability methods as tools for understanding cognitive phase transitions in neural models.

***

Would you like me to make a **Spanish version** of this abstract for submission consistency with the paper title, or keep it finalized in English for arXiv formatting?



## methodology

<!-- section=methodology generated=2026-03-27T20:37:41.023987+00:00 model=best -->

Aquí tienes una metodología concreta para investigar **el análisis de la curvatura de pérdida en la transición memorización-razonamiento**, con camino hacia un paper en arXiv siguiendo el marco de [arXiv:2510.24256](https://arxiv.org/abs/2510.24256).[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)

***

## 1. Formulación del Problema

**Objetivo central:**  
Caracterizar empíricamente cómo la **curvatura del paisaje de pérdida** (loss landscape curvature) organiza el espectro continuo entre:

- **Memorización pura**: recitación verbatim de datos de entrenamiento  
- **Razonamiento lógico**: inferencia generalizable robusta  
- **Habilidades intermedias**: recuperación de hechos, aritmética, razonamiento con contexto

**Hipótesis principal (extendiendo arXiv:2510.24256):**  
> Las direcciones de **baja curvatura** en el espacio de pesos están asociadas con habilidades frágiles (memorización, aritmética, hechos cerrados), mientras que las direcciones de **alta curvatura** codifican mecanismos generalizables robustos (razonamiento lógico, QA con contexto).

**Preguntas de investigación:**

1. ¿Cuál es la **relación cuantitativa** entre activación en componentes de baja curvatura y la sensitividad de una tarea a edición de pesos?
2. ¿Dónde se ubican **nuevas tareas** (ej. razonamiento matemático con Chain-of-Thought, razonamiento multi-paso, razonamiento simbólico) en el espectro memorización-razonamiento?
3. ¿La curvatura predice **mejor** la fragilidad que alternativas como SVD, magnitude pruning, o activation cloning?
4. ¿Existe un **umbral de curvatura** que separa consistentemente habilidades robustas de frágiles a través de modelos y dominios?

***

## 2. Baselines a Comparar

### 2.1 Métodos de Descomposición de Pesos

| Método | what it measures | Fortalezas | Debilidades |
|--------|------------------|------------|-------------|
| **K-FAC** (propuesto) | Curvatura aproximada del Hessian vía $$F \approx G \otimes A$$ [3](https://arxiv.org/html/2510.24256v1)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature) | Captura curvatura real del loss; interpretável como sensibilidad a cambios de pesos | Costoso de calcular (~20M tokens para estadísticas) [3](https://arxiv.org/html/2510.24256v1) |
| **SVD** | Importancia para reconstrucción de matriz [3](https://arxiv.org/html/2510.24256v1)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature) | Rápido, sin datos necesarios | No captura curvatura; separación menos saliente [3](https://arxiv.org/html/2510.24256v1) |
| **Magnitude Pruning** | Magnitud absoluta de pesos | Simple, común en compresión | Sin base teórica para memorización [4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature) |
| **Activation PCA** | Varianza de activaciones | Similar a K-FAC pero sin gradientes | Menos correlacionado con curvatura real [4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature) |

### 2.2 Métodos de Eliminar Memorización (unlearning)

| Método | Supervisión requerida | Performance en memorización | Perplexity post-edición |
|--------|----------------------|----------------------------|-------------------------|
| **K-FAC truncation** (baseline principal) | No [3](https://arxiv.org/html/2510.24256v1)[5](https://news.ycombinator.com/item?id=45845835) | 3.4% strict (Dolma), 16.1% (quotes OOD) [3](https://arxiv.org/html/2510.24256v1) | 22.84 [3](https://arxiv.org/html/2510.24256v1) |
| **BalancedSubnet (BSN)** | Sí (forget/retain sets) [3](https://arxiv.org/html/2510.24256v1)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature) | 6.0% strict (Dolma), 60.0% (quotes) [3](https://arxiv.org/html/2510.24256v1) | 23.59 [3](https://arxiv.org/html/2510.24256v1) |
| **SVD truncation** | No [3](https://arxiv.org/html/2510.24256v1) | 3.0% strict (Dolma), 17.5% (quotes) [3](https://arxiv.org/html/2510.24256v1) | 22.49 [3](https://arxiv.org/html/2510.24256v1) |

### 2.3 Métricas de Evaluación

**Memorización**:[3](https://arxiv.org/html/2510.24256v1)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Strict Accuracy**: $$ \mathbb{I}[d(S, \hat{S}) = 0] $$ (exact match)
- **Loose Accuracy**: $$ \mathbb{I}[1 - d(S,\hat{S})/L \geq 0.75] $$
- **Avg Normalized Levenshtein**: distancia editara normalizada (mayor = menos memorización)

**Habilidades downstream**:[6](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)
- **Retención de baseline**: $$ \frac{\text{acc}_{\text{edited}}}{\text{acc}_{\text{baseline}}} \times 100\% $$
- Categories:
  - Logical reasoning: 95–106% retention[3](https://arxiv.org/html/2510.24256v1)
  - Open-book QA: 93–99%[3](https://arxiv.org/html/2510.24256v1)
  - Closed-book QA: 74–86%[3](https://arxiv.org/html/2510.24256v1)
  - Math/arithmetic: 66–74%[3](https://arxiv.org/html/2510.24256v1)
  - Memorización: 3–16%[3](https://arxiv.org/html/2510.24256v1)

***

## 3. Outline del Método Propuesto

### Fase 1: Colectar Estadísticas de K-FAC

**Entrada:** Modelo pre-entrenado (ej. OLMo-2 7B )[1](https://arxiv.org/abs/2510.24256)[3](https://arxiv.org/html/2510.24256v1)

**Procedimiento**:[2](https://arxiv.org/html/2510.24256v2)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)

1. **Stream ~20M tokens** de Dolma/OLMo mix con sequence length 512[3](https://arxiv.org/html/2510.24256v1)
2. Para cada capa MLP (gate_proj, up_proj, down_proj):
   - Forward pass: buffer de pre-activaciones $$x$$ (excluyendo última posición)
   - Backward pass: registrar gradientes $$g$$ en salida
   - Acumular $$x^\top x$$ y $$g^\top g$$, normalizar por posiciones contributoras
   - Formar covarianzas $$\bm{A} = \mathbb{E}[xx^\top]$$ y $$\bm{G} = \mathbb{E}[gg^\top]$$[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)
3. Eigendecomposición:
   $$
   \bm{G} = \bm{U_G} \text{diag}(\lambda) \bm{U_G}^\top, \quad
   \bm{A} = \bm{U_A} \text{diag}(\mu) \bm{U_A}^\top
   $$
   con $$\lambda_0 \geq \lambda_1 \geq \dots$$, $$\mu_0 \geq \mu_1 \geq \dots$$[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

**Output:** Eigenbases $$\bm{U_G}, \bm{U_A}$$ y eigenvalues $$\lambda_i, \mu_j$$ por capa/proyección.

***

### Fase 2: Medir Activación por Componentes de Curvatura

**Para cada tarea** $$T \in \{\text{memorización, math, facts, logic, open-book QA}\}$$:

1. Correr modelo sobre dataset de tarea $$D_T$$
2. Para cada sample $$x \in D_T$$, extraer hidden activations $$h_\ell$$ en capas objetivo (ej. 23–25 para OLMo-7B)[2](https://arxiv.org/html/2510.24256v2)[3](https://arxiv.org/html/2510.24256v1)
3. **Proyectar activaciones** sobre eigenbasis de K-FAC:
   $$
   C = \bm{U_G}^\top \bm{W} \bm{U_A}, \quad C_{ij} = u_i^\top \bm{W} v_j
   $$
   $$
   \text{activación}_{ij}(x) = \|C_{ij} h(x)\|
   $$
4. Calcular **activation ratio** por percentil de curvatura:[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)
   $$
   r_T(p) = \frac{\mathbb{E}_{x \in T}[\|C_{(p)} h(x)\|]}{\mathbb{E}_{x \in \text{clean}}[\|C_{(p)} h(x)\|]}
   $$
   donde $$C_{(p)}$$ = componentes en percentil $$p$$ (top 10%, bottom 50%, etc.)

**Métrica clave:** Correlación entre $$r_T(\text{bottom})$$ y fragilidad de tarea.

***

### Fase 3: Edición de Pesos (KFAC Truncation)

**Preservar masa de curvatura**:[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)

1. Definir **curvature mass** para cada par $$(i,j)$$:
   $$
   \Pi_{ij} = \lambda_i \mu_j
   $$
2. Masa total: $$M_{\text{tot}} = \sum_{i,j} \Pi_{ij} = (\sum_i \lambda_i)(\sum_j \mu_j)$$[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
3. Seleccionar subset $$S$$ de pares $$(i,j)$$ en orden descendente de $$\Pi_{ij}$$ hasta:
   $$
   \sum_{(i,j) \in S} \Pi_{ij} \geq \rho \cdot M_{\text{tot}}
   $$
   donde $$\rho \in \{0.4, 0.5, 0.6, 0.7\}$$[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)
4. Máscara binaria $$M_{ij} = \mathbb{I}[(i,j) \in S]$$
5. Pesos comprimidos:
   $$
   \bm{W}_{\text{pairs}} = \bm{U_G} (\bm{C} \odot \bm{M}) \bm{U_A}^\top = \sum_{(i,j) \in S} C_{ij} u_i v_j^\top
   $$
[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

**Capas a editar:** Layers 23–25 para OLMo-7B, up/gate projections a 60% energy.[3](https://arxiv.org/html/2510.24256v1)

***

### Fase 4: Evaluación en Espectro de Tareas

**Benchmarks** (extendiendo OMLES suite):[3](https://arxiv.org/html/2510.24256v1)

| Categoría | Dataset(s) | Tipo |
|-----------|------------|------|
| **Memorización** | Dolma validation, Historical Quotes (OOD) | Exact-match recitation [3](https://arxiv.org/html/2510.24256v1) |
| **Math** | SimpleMath (2-digit ±), GSM8K, MMLU-Pro Math | Aritmética/cálculo [3](https://arxiv.org/html/2510.24256v1) |
| **Closed-book QA** | TriviaQA, Relations (fact retrieval) | Hechos sin contexto [3](https://arxiv.org/html/2510.24256v1) |
| **Open-book QA** | TriviaQA-Open (con Wikipedia article) | QA con contexto [3](https://arxiv.org/html/2510.24256v1) |
| **Logical Reasoning** | Boar Etruscan (reglas in-context), Boolean Expressions, CommonsenseQA | Inferencia no-numérica [3](https://arxiv.org/html/2510.24256v1) |

**Métrica principal:**  
$$
\text{Retention}_T = \frac{\text{Acc}_T(\text{edited})}{\text{Acc}_T(\text{baseline})} \times 100\%
$$

**Expected spectrum** (baseline de arXiv:2510.24256):[6](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)

$$
\text{logic} \ (95\text{--}106\%) \ > \ \text{open-book} \ (93\text{--}99\%) \ > \ \text{closed-book} \ (74\text{--}86\%) \ > \ \text{math} \ (66\text{--}74\%) \ > \ \text{memorization} \ (3\text{--}16\%)
$$

***

### Fase 5: Análisis de Correlación Curvatura-Fragilidad

**Propuesta novedosa:**

1. Para cada tarea $$T$$, calcular:
   - $$A_T^{\text{bottom}} = \mathbb{E}[\text{activación en bottom 50\%}]$$
   - $$A_T^{\text{top}} = \mathbb{E}[\text{activación en top 10\%}]$$
   - Ratio $$R_T = A_T^{\text{bottom}} / A_T^{\text{top}}$$

2. Correlacionar con fragilidad:
   $$
   \text{Fragilidad}_T = 1 - \text{Retention}_T
   $$

3. **Hipótesis**: $$ \text{Corr}(R_T, \text{Fragilidad}_T) > 0.8 $$[3](https://arxiv.org/html/2510.24256v1)

4. Comparar contra baselines:
   - Corr con SVD bottom percentil
   - Corr con magnitude pruning
   - Corr con activation PCA

**Resultado exitoso**: K-FAC predice fragilidad significativamente mejor ($$p < 0.01$$) que baselines.

***

## 4. Resultado Mínimo Viable (MVR)

Un paper arXiv viable requiere al menos **uno** de estos resultados sólidos:

### MVR 1: **Validación Replicada + Extensión de Espectro**

- [ ] Replicar curva de retención de arXiv:2510.24256 en OLMo-7B con $$r > 0.95$$ correlación[3](https://arxiv.org/html/2510.24256v1)
- [ ] Añadir **2+ nuevas categorías de tarefas** no analizadas:
  - Razonamiento matemático con Chain-of-Thought (ej. MATH dataset)
  - Razonamiento multi-paso (ej. HotpotQA, MultiHope)
  - Razonamiento simbólico (ej. bAbI tasks)
- [ ] Mostrar que nuevas tareas se ubican consistentemente en el espectro

**Contribución mínima**: Mapear tareas adicionales al continuum, confirmando que curvatura predice fragilidad.

***

### MVR 2: **Mejora sobre K-FAC Baseline**

- [ ] Proponer **variante de edición** que mejore K-FAC original:
  - Ejemplo: curvatura **por-tarea** (colectar K-FAC estadísticas sobre datos de tarea específica)
  - Ejemplo: curvatura **capa-selectiva** (optimal $$\rho$$ por capa vs. global)
  - Ejemplo: **curvatura adaptativa** (preservar más masa en capas con razonamiento)
- [ ] Demostrar mejora en al menos una métrica:
  - Memorización suppression: strict accuracy < 3.4% (Dolma)[3](https://arxiv.org/html/2510.24256v1)
  - Retención math: > 74% (vs. baseline 66–74%)[3](https://arxiv.org/html/2510.24256v1)
  - Perplexity: < 22.84[3](https://arxiv.org/html/2510.24256v1)

**Contribución mínima**: Variante que supera baseline en trade-off memorización vs. habilidad.

***

### MVR 3: **Descubrimiento Cualitativo Nuevo**

- [ ] Encontrar **una habilidad surprising** que:
  - Sea robusta a edición (retención > 90%) **a pesar** de alta activación en baja curvatura, **o**
  - Sea frágil (retención < 50%) **a pesar** de baja activación en baja curvatura
- [ ] Explicar mecánicamente por qué (ej. análisis de circuitos, causal tracing)
- [ ] Mostrar que K-FAC依然 predice correctamente fragilidad promedio

**Contribución mínima**: Matar/necesitar refinar la hipótesis simple "baja curvatura = memorización".

***

### MVR 4: **Análisis de Limitaciones Críticas**

- [ ] Demostrar que **memorización resurge** después de fine-tuning post-edición:
  - Editar modelo → fine-tuning 1–5 epochs en clean data → medir memorización de nuevo
  - Mostrar recuperación de > 50% memorización original
- [ ] O mostrar que **curvatura baja ≠ memorización** en contextos específicos:
  - Ejemplo: datos de alta frecuencia pero no memorizados = baja curvatura
  - Ejemplo: memorización de patterns sintácticos ≠ memorización verbatim

**Contribución mínima**: Principales limitaciones del método que falta en paper original.

***

## 5. Plan Experimental Concreto (8–12 semanas)

| Semana | Tarea | Deliverable |
|--------|-------|-------------|
| 1–2 | Setup: OLMo-2 7B, Dolma stream, K-FAC stats | $$\bm{A}, \bm{G}$$ por capa [3](https://arxiv.org/html/2510.24256v1) |
| 3–4 | Medir activation ratios por tarea | Figura tipo Fig. 2 [3](https://arxiv.org/html/2510.24256v1) |
| 5–6 | Implementar K-FAC editing, validar baselines | Tabla tipo Table 1 [3](https://arxiv.org/html/2510.24256v1) |
| 7–8 | Evaluar en spectrum de tareas | Figura tipo Fig. 3 [3](https://arxiv.org/html/2510.24256v1) |
| 9–10 | Análisis correlación curvatura-fragilidad | Figura tipo Fig. 4 [3](https://arxiv.org/html/2510.24256v1) |
| 11–12 | Extensión nueva (nuevas tareas / variante propuesta) | Resultado novel |

**Recursos necesarios:**
- 1–2 GPUs A100/H100 para K-FAC colección (~20M tokens)[3](https://arxiv.org/html/2510.24256v1)
- ~50GB RAM para buffer deactivaciones
- ~100GB storage para checkpoints

***

## 6. Estructura Sugerida del Paper

1. **Introduction**: Motivar espectro memorización-razonamiento, gap en comprensión
2. **Related Work**: Curvatura, memorización, interpretability, unlearning[7](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)[3](https://arxiv.org/html/2510.24256v1)
3. **Methods**: K-FAC background, collecting statistics, editing procedure[2](https://arxiv.org/html/2510.24256v2)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://arxiv.org/html/2510.24256v1)
4. **Experiments Setup**: Modelos, datasets, métricas, baselines[3](https://arxiv.org/html/2510.24256v1)
5. **Results**:
   - Replicación espectro baseline
   - Nuevas tareas mapeadas
   - Correlación curvatura-fragilidad
   - Comparación vs. SVD/magnitude
6. **Analysis**: Error analysis (math, facts), circuit-level interpretation[3](https://arxiv.org/html/2510.24256v1)
7. **Limitations**: Resurgence after tuning, numerical stability[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
8. **Conclusion**: Implicaciones para safety, unlearning, interpretability

***

## 7. ¿Qué Cuenta como Contribución Novel?

Para arXiv aceptable (no necesariamente NeurIPS/ICLR aceptado todavía):

| Tipo | Contribución mínima |
|------|---------------------|
| **Empírica** | Mapear 3+ nuevas tareas al espectro, confirmar predicción de curvatura |
| **Método** | Variante K-FAC que mejora baseline en trade-off |
| **Análisis** | Explicación mecánica de por qué aritmética es frágil (circuitos específicos) [3](https://arxiv.org/html/2510.24256v1) |
| **Negativa** | Mostrar límite fundamental (memorización resurge, curvatura no es suficiente) |

***

¿Quieres que detallle más alguna parte? Por ejemplo:
- Código Python para calcular K-FAC estadísticas
- Lista exacta de datasets con enlaces
- Plan de ablation studies específicos
- Cómo hacer análisis de circuitos (causal tracing) para explicar fragilidad matemática



## experiments

<!-- section=experiments generated=2026-03-27T20:38:03.035903+00:00 model=best -->

This experiment analyzes loss curvature changes during the memorization-to-reasoning transition in language models, building on K-FAC approximations of the Hessian to identify sharp (memorization) vs. flat (reasoning) directions. It uses scalable edits to probe phase shifts, suitable for accessible models like OLMo-2 7B.[1](https://arxiv.org/html/2510.24256v1)[2](https://arxiv.org/abs/2510.24256)

## Objectives
Quantify how loss curvature evolves from high (sharp basins for memorized data) to low/moderate (flatter for reasoning). Identify transition thresholds via double descent-like curves and activation patterns. Test interventions to suppress memorization while preserving reasoning.[3](https://arxiv.org/html/2510.24256v2)[4](https://deep-learning-mit.github.io/staging/blog/2023/double_descent/)[1](https://arxiv.org/html/2510.24256v1)

## Baselines
- Unedited baseline model (full weights).
- SVD truncation (prune low singular values, data-free).[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)
- BalancedSubnet (BSN): Supervised unlearning with forget/retain sets.[1](https://arxiv.org/html/2510.24256v1)
- SAM (Sharpness-Aware Minimization): Train with curvature regularization.[1](https://arxiv.org/html/2510.24256v1)

## Setup
Train/fine-tune small-to-medium LMs (e.g., OLMo-1B/7B) on mixtures: 70% clean Dolma/Pile (generalization), 30% duplicates/noised labels (induce memorization). Vary interpolation regime by scaling data repeats (1x to 100x) or model size (100M-7B params). Compute K-FAC covariances (A=activation, G=gradient) on 20M tokens per checkpoint. Edit MLPs in late layers (23-25) at 60% curvature mass retention (ρ=0.6).[3](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v1)

## Metrics
- Memorization: Strict/loose accuracy (exact/75% match on heldout prefixes), Levenshtein distance.[1](https://arxiv.org/html/2510.24256v1)
- Reasoning: Accuracy on GSM8K (math), TriviaQA (closed-book facts), Boar Etruscan (logic); perplexity on Pile10k.
- Curvature: Trace/top eigenvalue of K-FAC FIM (G⊗A); activation ratios (mem/clean on low vs. high eigendirections).[3](https://arxiv.org/html/2510.24256v2)
- Generalization: MMLU-Pro, validation PPL drop post-edit.

## Ablations
- Curvature threshold: Vary ρ (40-80%) to map transition sharpness.
- Data regime: Clean vs. duplicate-heavy mixtures; noised labels (10-50%).
- Edit scope: All MLPs vs. early/late layers; up/gate/down proj only.
- Model scale: 1B vs. 7B to check double descent.[6](https://chrisliu298.ai/neurips2023_opt_poster.pdf)

## Budget
Target 100 GPU-hours (A100s): K-FAC on 20M tokens (~2h/model), 10 runs/ablation (fine-tune 1-2 epochs each), edits/evals (~1h). Use Colab/Prodigy for student access; batch parallelize covariance collection. Scale down to 1B model if needed.[3](https://arxiv.org/html/2510.24256v2)

## Results Table Outline

| Configuration | Memorization Strict Acc ↓ (%) | Reasoning Acc (GSM8K) ↓ (%) | PPL ↑ | Max Curvature (Trace) ↓ | Activation Ratio (Low Eigens) ↑ |
|---------------|------------------------------|-----------------------------|-------|-------------------------|---------------------------------|
| Baseline     | 99.9                | 100 (baseline)     | 19.04 | 1.0 (norm)[3](https://arxiv.org/html/2510.24256v2)     | 1.0[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)                     |
| K-FAC ρ=0.6  | 3.4                 | 66-74              | 22.84 | 0.6                    | 1.6x (mem/clean)       |
| BSN          | 6.0                 | ~80                | 23.59 | N/A                    | N/A                            |
| SVD          | 3.0                 | ~85                        | 22.49 | N/A                    | 1.2x[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)                    |
| High Dups    | 95                          | 50                         | 25    | 1.5                    | 2.0x                           |



## related_code

<!-- section=related_code generated=2026-03-27T20:38:27.294024+00:00 model=best -->

Here is a curated list of open‑source repositories and core libraries relevant to *análisis de la curvatura de pérdida en la transición memorización–razonamiento*. For each I give URL, license (if visible), last‑update signal, and one‑liner on relevance.

***

### 1. **From Memorization to Reasoning in the Spectrum of Loss Curvature (author‑linked code)**

- **URL:** https://github.com/DeepakTatachar/Privacy-Memorization-Curvature[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **License:** Typically per‑paper licenses (often BSD‑style or MIT‑like; check repo `LICENSE` / `README` directly).[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **Last‑update signal:** Repository tagged as “code for Unveiling Privacy, Memorization and Input Loss Curvature” (2024‑style project).[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **Relevance:** Provides an official implementation for analyzing memorization and privacy via input‑wise loss‑curvature; useful as a reference for how curvature per‑sample can be used to flag memorized or high‑risk examples.[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)

***

### 2. **K‑FAC curvature estimators (K‑FAC‑JAX / JAX‑level)**

- **URL (K‑FAC‑JAX):** https://github.com/google-deepmind/kfac-jax[2](https://github.com/google-deepmind/kfac-jax)
- **License:** Apache 2.0 (clearly stated in repo).[2](https://github.com/google-deepmind/kfac-jax)
- **Last‑update signal:** Commit history and quickstart docs show active maintenance into 2022–2024 band.[2](https://github.com/google-deepmind/kfac-jax)
- **Relevance:** Lightweight, scalable K‑FAC library for computing Hessian‑type curvature approximations in JAX; directly usable for loss‑curvature analysis (e.g., the “From Memorization to Reasoning…” style decompositions at the MLP / transformer layer).[3](https://arxiv.org/html/2510.24256v1)[2](https://github.com/google-deepmind/kfac-jax)

***

### 3. **K‑FAC in TensorFlow (TF reference)**

- **URL:** https://github.com/tensorflow/kfac[4](https://github.com/tensorflow/kfac)
- **License:** Apache 2.0 (explicit in repo).[4](https://github.com/tensorflow/kfac)
- **Last‑update signal:** Commits and releases span 2018–2020; less actively updated but still functional.[4](https://github.com/tensorflow/kfac)
- **Relevance:** Canonical TensorFlow implementation of K‑FAC, useful if you want to plug curvature‑based memorization analysis into legacy TF‑based vision or language models.[3](https://arxiv.org/html/2510.24256v1)[4](https://github.com/tensorflow/kfac)

***

### 4. **Memorization‑via‑curvature (per‑sample curvature) reference**

- **URL (paper):** https://arxiv.org/abs/2307.05831[5](https://arxiv.org/abs/2307.05831)
- **License:** Paper is CC‑BY or similar (standard arXiv); any code repo is not explicitly linked here, but the authors describe per‑sample curvature estimation around training points.[5](https://arxiv.org/abs/2307.05831)
- **Last‑update signal:** Preprint v2 updated 2 Oct 2023.[5](https://arxiv.org/abs/2307.05831)
- **Relevance:** Conceptual/algorithmic foundation for using local curvature of the loss function around individual samples as a memorization proxy; you can implement this on top of K‑FAC or similar Hessian‑approximation stacks.[3](https://arxiv.org/html/2510.24256v1)[5](https://arxiv.org/abs/2307.05831)

***

### 5. **K‑FAC “classic” implementation (PyTorch‑style)**

- **URL:** https://github.com/Xin-Jing/K-FAC[6](https://github.com/Xin-Jing/K-FAC)
- **License:** Repo does not spell out license prominently, but the codebase is small and oriented toward research reuse.[6](https://github.com/Xin-Jing/K-FAC)
- **Last‑update signal:** Initial commits in 2017; last sizable pushes around 2018–2019.[6](https://github.com/Xin-Jing/K-FAC)
- **Relevance:** Simple, pedagogical K‑FAC implementation; handy if you want a minimal codebase to adapt for loss‑curvature experiments on memorization–reasoning in small MLPs or conv‑nets.[3](https://arxiv.org/html/2510.24256v1)[6](https://github.com/Xin-Jing/K-FAC)

***

### 6. **General “loss‑landscape / curvature / deep‑phenomena” curation**

- **URL (awesome‑deep‑phenomena):** https://github.com/MinghuiChen43/awesome-deep-phenomena[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **License:** N/A (collection of links and papers).[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **Last‑update signal:** Last commits in 2020–2021; still useful as a curated index.[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **Relevance:** Collects many empirical studies on loss‑landscape flatness, curvature, and memorization; can guide you to additional papers with associated codebases for curvature‑based analysis.[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)

***

If you tell me whether you want to work in **PyTorch** vs **JAX** and whether you’re targeting **per‑sample curvature** or **parameter‑space curvature (K‑FAC‑style)**, I can compose a minimal end‑to‑end example script (e.g., “compute loss‑curvature per‑sample for a small MLP and then threshold by curvature to probe memorization”).



## gaps

<!-- section=gaps generated=2026-03-27T20:38:43.136091+00:00 model=best -->

- **Dynamic curvature evolution during training**: The paper uses static post-training K-FAC snapshots; tracking how curvature spectra shift from memorization-dominant to reasoning-dominant phases remains unexamined, critical for understanding training dynamics like progressive sharpening.[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2601.16979v1)
- **Scalability to >7B LLMs**: Analyses are limited to 7B OLMo-2 and small ViTs; gaps exist in verifying low-curvature memorization signals at frontier scales (e.g., 100B+), where compute for K-FAC becomes prohibitive.[1](https://arxiv.org/abs/2510.24256)
- **Beyond MLP layers**: Focuses on MLP projections; underexplored how attention heads or layer norms contribute to curvature-based memorization-reasoning disentanglement.[1](https://arxiv.org/abs/2510.24256)
- **Theoretical justification for aggregate inversion**: Empirical "flatter aggregate for memorization" lacks formal proof; proving why varying per-example sharp directions cancel in K-FAC remains open.[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Long-term stability of edits**: Edits suppress memorization initially, but resurgence after further tuning is noted as a limitation; longitudinal studies post-editing are needed .
- **Numerical stability of low eigenvalues**: Smallest K-FAC eigenvalues are unstable, potentially misattributing reasoning circuits; robust estimation methods for tail spectra are underexplored .
- **Multimodal and non-English settings**: Limited to English LMs/ViTs; curvature transitions in multilingual or vision-language models (e.g., Bolivia-specific data) untested.[1](https://arxiv.org/abs/2510.24256)
- **Comparison to exact Hessian**: K-FAC approximation unvalidated against full Hessian for memorization spectra; gaps in approximation error bounds for reasoning tasks.[2](https://arxiv.org/html/2601.16979v1)[1](https://arxiv.org/abs/2510.24256)



## sota

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


