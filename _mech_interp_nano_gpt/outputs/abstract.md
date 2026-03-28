<!-- section=abstract generated=2026-03-26T19:39:58.055621+00:00 model=best -->

A continuación te propongo un **abstract estructurado** para tu nota técnica, con formato pensado para **arXiv / blog**, enfocándote en **interpretabilidad mecanicista en modelos tipo nanoGPT pequeños, entrenables solo en CPU** (línea Olsson/Nanda/Anthropic, sin GPU). Las afirmaciones inciertas o exploratorias están marcadas explícitamente.

***

### Structured Abstract

**Background**  
Los modelos tipo nanoGPT demuestran que es posible entrenar transformers pequeños con rendimiento razonable en tareas de lenguaje usando solo CPU. Al mismo tiempo, la línea de *mechanistic interpretability* de Olsson/Nanda/Anthropic ha mostrado que en modelos más grandes se pueden aislar “circuitos” de atención y MLP responsables de comportamientos específicos, como la identificación de objetos indirectos (IOI), usando hooks de activación y *activation patching*.

**Gap**  
Sin embargo, aún no existe un **pipeline estándar y reproducible** para aplicar estas ideas a modelos tipo nanoGPT ultra‑pequeños entrenados *solo en CPU*. En particular, falta un protocolo claro para:  
- definir tareas IOI‑like adecuadas,  
- integrar hooks y patching en un flujo completamente CPU‑compatible,  
- y cuantificar de forma operable la noción de “circuitos indirectos” en estas arquitecturas minimalistas.  
_[Marca de incertidumbre:]_ se supone que estas técnicas son portables a modelos pequeños, pero esto no se ha demostrado de forma sistemática en un entorno accesible.

**Method**  
Proponemos un **framework de interpretabilidad mecanicista** para nanoGPT‑style basado en:  
- un modelo pequeño (1–4 capas, 2–8 heads, 12M–50M parámetros) entrenado únicamente en CPU sobre un dataset IOI‑like sintético,  
- un sistema de **hooks de activación** que registra residual streams, outputs de atención y MLP en formato NumPy sin dependencia de GPU,  
- **activation patching** y una versión simplificada de *iterative circuit discovery* para aislar subgrafos mínimos de cabezas que resuelven IOI,  
- y una **métrica de indirectness** operable en CPU, definida como una combinación de número de heads, profundidad en capas y distancia posicional en el texto.  
_[Marca de incertidumbre: la métrica de indirectness es ad hoc y se asume plausible; su validez general dependerá de futuras comparaciones con otros marcos de interpretación.]_

**Results (placeholder / si aún no conoces los resultados)**  
_[Nota: completar con valores reales una vez ejecutados los experimentos.]_  
En un primer conjunto de experiencias, esperamos observar que:  
- modelos nanoGPT pequeños alcanzan **alta accuracy en tareas IOI‑like**, comparables a versiones más grandes en tareas análogas,  
- se pueden aislar **circuitos indirectos compactos** (1–3 heads en 1–2 capas) cuyo *patching* provoca caídas significativas de accuracy, mientras que el modelo aún resuelve tareas más simples (copia directa),  
- y que el **pipeline CPU‑only** propuesto es reproducible en máquinas sin GPU, permitiendo interpretar estos modelos en un entorno bajo‑recurso.  
_[Marca de incertidumbre: estos resultados esperados dependen de la estabilidad de las métricas de patching y de la capacidad del modelo pequeño para aprender el patrón IOI‑like; podrían no replicarse en todas las arquitecturas o tamaños de contexto.]_

**Conclusion**  
Este trabajo propone un **framework de interpretabilidad mecanicista reproduci­ble** para nanoGPT‑style entrenables solo en CPU, centrándose en circuitos indirectos, atención y hooks de activación. Si los resultados preliminares se confirman, el pipeline podría servir como **referencia para estudios de interpretabilidad accesibles** en hardware modesto, ayudando a reducir la brecha entre investigadores con y sin GPU, y ofreciendo un banco de pruebas para explorar cómo cambian los circuitos al reducir dramáticamente el tamaño y el presupuesto de entrenamiento.  
_[Marca de incertidumbre: la extensibilidad a tareas de lenguaje real más complejas sigue siendo un objetivo a mediano plazo, y no está garantizada por el diseño actual.]_

***

Si quieres, en el siguiente paso puedo ayudarte a **convertir esto en el primer párrafo de la introducción** del manuscrito, manteniendo el mismo nivel de detalle y marcando claramente lo que se sabe vs. lo que se propone.
