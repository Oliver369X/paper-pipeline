<!-- section=limitations generated=2026-03-26T19:40:40.023723+00:00 model=best -->

A continuación van limitaciones y amenazas a la validez claras y concretas para tu trabajo de interpretabilidad mecanicista en modelos tipo nanoGPT pequeños, entrenables solo en CPU:

***

### 1) Limitaciones de alcance (scope)

- **Tareas altamente sintéticas (IOI‑like)**  
  El enfoque se centra en tareas simbólicas simplificadas (ej. IOI) con patrones de copia y supresión muy limpios; esto **limita la generalización a comportamientos reales de lenguaje natural**, donde el razonamiento es más compositivo y ambiguo.

- **Modelos muy pequeños**  
  Los modelos de 1–4 capas y 12M–50M parámetros capturan solo una fracción de lo que hacen modelos medianos/grandes; **no se puede asumir que los circuitos encontrados escalarán** en estructura o interpretabilidad.

- **Foco en CPU‑only**  
  El diseño explícito de no usar GPU simplifica el acceso, pero **limita el tipo y tamaño de experimentos posibles** (por ejemplo, SAEs densos, modelos de más capas, o análisis de largos contextos).

***

### 2) Synthetic vs. real data

- **Generalización limitada a lenguaje real**  
  Las tareas IOI‑like y otros datasets sintéticos se construyen para aislar comportamientos específicos; el hecho de que un circuito indirecto funcione ahí **no implica que sea representativo** de cómo se organizan las representaciones en corpus reales (noticias, discursos, etc.).

- **Dataset muy estilizado**  
  Los patrones de nombres/objetos se generan procedimentalmente, con baja diversidad lingüística y casi sin variación de estilo o género; esto **introduce un sesgo hacia patrones artificiales** que pueden no reflejar el desafío real de interpretabilidad en lenguaje natural.

- **Riesgo de over‑fitting interpretacional**  
  Al diseñar la tarea y luego buscar un circuito que explique exactamente ese patrón, existe el riesgo de **sobre‑interpretar ruido o artefactos de entrenamiento** como si fueran principios universales del modelo.

***

### 3) Limitaciones de las afirmaciones de interpretabilidad

- **“Circuito” como descripción, no garantía causal**  
  El uso de *activation patching* y *iterative pruning* ayuda a aislar subgrafos de cabezas, pero **no prueba que el circuito sea el único mecanismo posible**; el modelo puede tener caminos redundantes o alternativos no detectados por el método.

- **Métrica de indirectness ad hoc**  
  La métrica de indirectness (número de heads, profundidad de capas, distancia posicional) es **heurística y no validada** contra marcos formales de causalidad; su correlación con el impacto funcional podría ser empírica pero débil en algunos configuraciones.

- **Riesgo de confundir correlación con mecanismo**  
  Observar que parchear un head o capa reduce la precisión **no demuestra que el modelo “piense” en términos de ese circuito**; solo muestra que esa ruta es funcionalmente importante en el conjunto de datos usado.

- **Superposición y polisemicidad poco exploradas**  
  En modelos pequeños se puede encontrar un circuito relativamente “limpio”, pero **esto no garantiza ausencia de superposición**; el mismo head o dirección de residuo podría estar implementando simultáneamente otros patrones que el análisis no revela.

***

### 4) Cosas que requieren GPU o modelos más grandes

- **Sparse / dense autoencoders (SAEs) en varias capas**  
  Aplicar SAEs a muchas capas del modelo (en especial en modelos de tamaño intermedio) suele ser **muy costoso en memoria y computación**, y en la práctica depende de GPU para entrenar y analizar.

- **Análisis de largos contextos o modelos de más capas**  
  Expandir el enfoque a modelos de 6–12 capas o contextos de 512+ tokens en CPU **vuelve inviable guardar todas las activaciones** y realizar múltiples análisis de patching sin largos tiempos de E/S y consumo de RAM.

- **Transferencia a modelos de producción**  
  Modelos de lenguaje reales usados en la práctica (incluso “pequeños” de 1B+ parámetros) **no caben en CPU modestas** ni se entrenan eficientemente sin GPU; por tanto, el pipeline descrito debe verse como **prueba de concepto para nanoGPT, no como solución directa a modelos de producción**.

- **Extrapolación de hallazgos a arquitecturas más complejas**  
  Lo que se observa en arquitecturas minimalistas (atención‑only, pocas capas, MLP pequeño) **no implica que comportamientos similares existan de la misma forma en GPT‑2, LLaMA‑style u otros modelos**, donde la densidad de circuitos, superposición y ruido son mucho mayores.

***

Estas limitaciones son todas **compatibles con un tono de nota técnica**: puedes presentar el trabajo como un **paso útil pero local** en el mapa de interpretabilidad mecanicista, explícitamente restringido a modelos pequeños, datos sintéticos y CPU‑only.
