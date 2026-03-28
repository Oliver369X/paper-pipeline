<!-- section=gaps generated=2026-03-26T19:30:30.229101+00:00 model=best -->

A continuación van **problemas abiertos y brechas metodológicas** específicamente relevantes para **interpretabilidad mecanicista en modelos tipo nanoGPT pequeños, entrenables solo en CPU, con foco en circuitos indirectos, atención y hooks de activación (línea Olsson/Nanda/Anthropic)**. Están formulados como bullets, pensados para orientar una nota técnica reproducible (arXiv / blog).

- **Falta de protocolos estándar para “circuitos indirectos” en nanoGPT‑style**  
  No existe un conjunto de pruebas/decisiones operativas (datasets sintéticos, métricas, criterios de “indirecto vs. directo”) adaptado a GPTs pequeños y entrenables en CPU, lo que dificulta comparar resultados de forma reproducible.[1](https://www.alignmentforum.org/posts/LbrPTJ4fmABEdEnLf/200-concrete-open-problems-in-mechanistic-interpretability)[2](https://arxiv.org/abs/2407.02646)

- **Escasos benchmarks de IOI‑like en modelos muy pequeños (≈1–4 capas, solo atención/MLP básicos)**  
  La mayoría de circuitos de IOI se estudian en GPT‑2 Small o modelos más grandes; hay pocos benchmarks listos para usar en arquitecturas tipo nanoGPT minimalistas, limitando la reutilización de resultados.[3](https://arxiv.org/pdf/2510.25013.pdf)[1](https://www.alignmentforum.org/posts/LbrPTJ4fmABEdEnLf/200-concrete-open-problems-in-mechanistic-interpretability)

- **Ausencia de “pipeline CPU‑only” end‑to‑end para hooks + patching + circuit‑discovery**  
  Aunque se sabe que hooks y patching pueden correr en CPU, no hay un flujo de trabajo documentado y modular (guardado de activaciones, versionado de hooks, análisis estadístico) pensado para máquinas sin GPU, lo que dificulta la reproducibilidad comunitaria.[4](https://www.coairesearch.org/blog/democratizing-mechanistic-interpretability-bringing-neural-network-analysis-to-apple-silicon)[5](https://coairesearch.org/notes/democratizing-mechinterp/)

- **Poco estudio de cómo cambian los circuitos cuando se reduce dramáticamente el tamaño/architect y el budget**  
  No se entiende bien cómo se degradan o reorganizan los circuitos indirectos (por ejemplo, cabezas de copia‑inducción) al pasar de modelos medianos a nanoGPT ultra‑pequeños; esto limita la extrapolación de hallazgos previos.[6](https://rohanhitchcock.com/notes/2023-6-slt-alignment-talk-mech-interp.pdf)[2](https://arxiv.org/abs/2407.02646)

- **Indirect circuits en tareas no‑simbólicas (lenguaje “real”) son poco explorados en modelos pequeños**  
  La mayoría de trabajo en circuitos indirectos se centra en tareas simbólicas (IOI, modular addition, etc.); se sabe poco de qué tan “indirectos” son los circuitos en nanoGPT entrenado en corpus reales (sin GPU), y qué patrones recursivos aparecen.[7](https://www.scribd.com/document/895040041/2407-02646v3)[3](https://arxiv.org/pdf/2510.25013.pdf)

- **Falta de tipologías de circuitos indirectos basadas en atención y res stream en nanoGPT**  
  No hay taxonomías claras de “patrones de circuito” en pequeña escala (p.ej., tipos de caminos atención‑residual‑MLP) que se puedan usar para describir y comparar modelos reproduciblemente en notas técnicas.[2](https://arxiv.org/abs/2407.02646)[1](https://www.alignmentforum.org/posts/LbrPTJ4fmABEdEnLf/200-concrete-open-problems-in-mechanistic-interpretability)

- **Ausencia de una métrica robusta de “indirectness” operable en CPU‑only**  
  No hay consenso ni métrica práctica para cuantificar cuán “indirecto” es un circuito (por ejemplo, número de pasos, dependencia funcional, causalidad estimada) que sea factible calcular en modelos pequeños sin GPU dedicada.[8](https://arxiv.org/html/2501.16496v1)[2](https://arxiv.org/abs/2407.02646)

- **GAP en conectividad entre interpretabilidad mecanicista y técnicas de edición/steering en modelos pequeños**  
  Aunque se sabe cómo editar circuitos en modelos grandes, hay poca literatura sobre cómo adaptar técnicas de **model editing** o **repertoire engineering** a nanoGPT‑style sin GPU, lo que limita aplicaciones prácticas de la nota técnica.[9](https://ai-frontiers.org/articles/the-misguided-quest-for-mechanistic-ai-interpretability)[2](https://arxiv.org/abs/2407.02646)

- **Escasa integración de SAEs/sparse features en CPU‑only nanoGPT workflows**  
  Sparse autoencoders y feature‑engineering son muy útiles, pero su aplicación a modelos pequeños es poco documentada y suele asumir GPU; falta un flujo de trabajo CPU‑friendly que sea reproducible y pedagógico.[10](https://arxiv.org/html/2410.16443v3)[2](https://arxiv.org/abs/2407.02646)

- **Poca exploración de la superposición (superposition) en modelos tipo nanoGPT entrenados en CPU**  
  Se sabe que la superposición es un límite clave de la interpretabilidad, pero no hay muchos estudios focalizados en cómo se presenta en nanoGPT‑style con pocos parámetros, y con qué métodos se puede reducir o explicar.[11](https://www.youtube.com/watch?v=ZSg4-H8L6Ec)[2](https://arxiv.org/abs/2407.02646)

- **Falta de estándares de validación/replicabilidad específicos para notas técnicas en mech‑interp**  
  No hay plantillas claras de “cómo se debe reportar” un circuito encontrado en un nanoGPT (level de detalle, tests de robustez, versionado de código/hooking) orientadas a publicaciones breve en arXiv / blog.[7](https://www.scribd.com/document/895040041/2407-02646v3)[2](https://arxiv.org/abs/2407.02646)

- **Casi ningún trabajo muestra cómo variar hiperparámetros (arquitectura, tamaño, lr) afecta la localización y estructura de circuitos indirectos**  
  Conocer cómo cambiar capas, heads, embedding‑dim, etc., en un modelo pequeño y CPU‑only repercute en la naturaleza de los circuitos sería muy útil para diseño de experimentos reproductibles, pero esta analítica es rara.[6](https://rohanhitchcock.com/notes/2023-6-slt-alignment-talk-mech-interp.pdf)[2](https://arxiv.org/abs/2407.02646)

- **Brecha metodológica entre “circuito” y “causalidad/mechanismo formal” en modelos pequeños**  
  Aunque se describen “circuitos”, rara vez se vinculan claramente con marcos formales de causalidad o mediación; esto debilita la fuerza de las notas técnicas que quieren ser más que descriptivas.[12](https://far.ai/research/open-problems-in-mechanistic-interpretability)[8](https://arxiv.org/html/2501.16496v1)

- **Escaso eco en la comunidad de “interpretación en la práctica” para nanoGPT-style CPU‑only**  
  La mayoría de guías prácticas asumen GPUs o modelos no‑nano; hay poca documentación de cómo organizar un proyecto de mech‑interp completo (desde entrenamiento hasta hooks, análisis y visualización) en hardware limitado.[5](https://coairesearch.org/notes/democratizing-mechinterp/)[4](https://www.coairesearch.org/blog/democratizing-mechanistic-interpretability-bringing-neural-network-analysis-to-apple-silicon)

Si quieres, en el siguiente paso puedo ayudarte a **convertir 3–4 de estos puntos en una hoja de ruta de experimentos** para tu nota técnica (por ejemplo, “benchmark de IOI en nanoGPT‑style CPU” + “métrica de indirectness” + “pipeline estándar de hooks”).
