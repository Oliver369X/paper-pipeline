<!-- brain_brief ts=2026-03-27T18:02:47.860864+00:00 -->

# Brief Doctoral: Curvatura de Pérdida y Supresión de Memorización (K-FAC)

## 1. Visión General del Paper (arXiv:2510.24256)
El trabajo de Merullo et al. propone un cambio de paradigma en el análisis de la memorización: en lugar de buscar 'neuronas' de memoria, analizan la **curvatura del paisaje de pérdida**. Utilizando la aproximación **K-FAC (Kronecker-factored Approximate Curvature)** de la matriz de Fisher, logran descomponer los pesos en direcciones que corresponden a generalización (alta curvatura) y memorización (direcciones planas o de baja curvatura que varían por ejemplo).

### Hallazgos Clave:
- **Direcciones de Memoria:** Los puntos memorizados (recitación verbatim) se alinean con direcciones de curvatura más agudas localmente, pero que al promediarse resultan planas. 
- **Edición por Curvatura:** Al proyectar los pesos y aplicar una máscara que conserva solo el top de la 'masa de curvatura' (energía), se puede eliminar la capacidad de recitar textos específicos (Dolma, Quotes) sin destruir la capacidad de razonamiento o el lenguaje general.
- **Fragilidad del Razonamiento:** A diferencia de la memorización, las tareas de aritmética y recuperación de hechos (factual recall) dependen de direcciones de curvatura muy específicas y frágiles; editarlas degrada severamente estas capacidades.

## 2. Estrategia de Replicación
Para la réplica, utilizaremos el entorno de `paper-pipeline` con los siguientes pasos:
1. **Recolección de Estadísticas:** Simular la recolección de covarianzas de gradientes y activaciones para obtener la aproximación de Fisher en capas críticas (ej. capas medias/finales de OLMo).
2. **Eigendecomposición:** Implementar el cálculo de autovalores y autovectores en el espacio factorizado (K-FAC) para identificar las direcciones de baja curvatura.
3. **Métrica de Evaluación:** Implementar el 'Strict Accuracy' para prefijos conocidos y medir la Perplexity (PPL) en datasets neutrales (Pile/Wikitext) para asegurar que el modelo no se degrade.

## 3. Hipótesis de Investigación Propuesta
**Hipótesis:** "La técnica de edición por curvatura K-FAC mostrará una selectividad significativamente mayor en modelos multimodales pequeños (ej. Phi-3-Vision) al separar la memorización de datos de entrenamiento (texto verbatim) de la capacidad de razonamiento visual (VQA), sugiriendo que la curvatura codifica invariantes semánticas independientemente de la modalidad de entrada."
- **Racional:** El paper original menciona brevemente ViTs, pero no explora si la edición en la parte de lenguaje afecta el razonamiento sobre tokens visuales. Si la hipótesis se confirma, K-FAC sería una herramienta vital para 'des-memorizar' modelos multimodales sin perder su utilidad lógica.

## 4. Riesgos y Límites
- **Costo Computacional:** La descomposición K-FAC en modelos de 7B requiere memoria significativa (A100 recomendada). Se sugiere empezar con versiones de 1B.
- **Inestabilidad:** Ajustar el umbral de energía (ρ=0.6) es crítico; una desviación pequeña puede colapsar la Perplexity del modelo.
