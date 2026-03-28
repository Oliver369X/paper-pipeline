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
