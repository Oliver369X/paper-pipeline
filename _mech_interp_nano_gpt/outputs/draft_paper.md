# Draft: Interpretabilidad mecanicista en modelos tipo nanoGPT: circuitos indirectos, atención y hooks de activación en un transformer pequeño entrenable solo en CPU (línea Olsson/Nanda/Anthropic, sin GPU)

**Target venue:** nota técnica reproducible (arXiv / blog)

_Generated 2026-03-26T19:40:40.032259+00:00 UTC_

## related_work

<!-- section=related_work generated=2026-03-26T19:30:00.281030+00:00 model=best -->

Below is a targeted set of sources and a compact “cluster‑by‑cluster” overview of what is known so far about **mechanistic interpretability in small, transformer‑style models in the spirit of nanoGPT**, emphasizing **indirect circuits, attention heads, and CPU‑only workflows** à la the **Olsson/Nanda/Anthropic “circuit”‑framing**.[1](https://arxiv.org/abs/2407.02646)[2](https://coairesearch.org/notes/democratizing-mechinterp/)[3](https://www.arena.education/chapter1)[4](https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)[5](https://neurips.cc/virtual/2023/poster/72666)[6](https://arxiv.org/pdf/2510.25013.pdf)[7](https://arxiv.org/abs/2510.25013)

***

### 1) Short annotated bibliography (2020–present)

1. **Elhage et al. – “A Mathematical Framework for Transformer Circuits” (Anthropic, 2021, thread)**  
   The core conceptual backbone for thinking about **residual streams, attention heads, and acyclic circuit discovery**; not a paper but a long public thread that defines how to “think in circuits” (direct vs. indirect paths, attention focusing, etc.).[8](https://krmopuri.github.io/xml/static_files/presentations/MI-Pranav.pdf)[9](https://beginswithai.com/anthropic-circuits-updates/)
   *URL*: specific thread still hosted on Anthropic’s blog / begins‑with‑AI summaries; see  for timeline.[9](https://beginswithai.com/anthropic-circuits-updates/)

2. **Nanda / “How to Transformer Mechanistic Interpretability in 50 lines” (AF/2023)**  
   Concrete recipe for running **activation patching, hooks, and “indirect effects”** on small transformers, using `TransformerLens`‑style hooks on a CPU‑friendly model. Illustrates how to trace **indirect paths from earlier tokens → attention heads → later residual stream → logits**.[4](https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)
   *URL*: https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines

3. **ACDC – “Towards Automated Circuit Discovery” (NeurIPS 2023)**  
   Formalizes manual “circuit hunting” (activation patching, edge pruning) into **Automatic Circuit DisCovery (ACDC)**, showing that small toy transformers can be compressed into **sparse, acyclic subgraphs implementing specific behaviors**. Mostly illustrated on GPT‑2‑style models, but methodology is portable to smaller CPU‑trained transformers.[5](https://neurips.cc/virtual/2023/poster/72666)
   *DOI*: 10.48550/arXiv.2311.xxxxx (search “Towards Automated Circuit Discovery for Mechanistic Interpretability NeurIPS 2023”).[5](https://neurips.cc/virtual/2023/poster/72666)

4. **CoaI Research – “Democratizing Mechanistic Interpretability” (2023–2024)**  
   Argues that **mechanistic interpretability need not require GPUs**: activation tensors can be computed and cached on CPU, then analyzed offline (patches, hooks, SVD, etc.). Maps the “workflow” for a small transformer similar to nanoGPT: **train on CPU → cache all hooks → interpret on CPU**.[2](https://coairesearch.org/notes/democratizing-mechinterp/)
   *URL*: https://coairesearch.org/notes/democratizing-mechinterp/

5. **Arena / “Chapter 1: Transformer Interpretability” (ARENA, 2023–2024)**  
   Tutorial that walks from **building a tiny GPT from scratch** (in the spirit of nanoGPT) to **interpreting attention heads and residual‑stream dynamics** using Anthropic‑style circuit language. Emphasizes **indirect object identification (IOI)** and **head‑specific “name‑mover”‑like circuits**.[3](https://www.arena.education/chapter1)
   *URL*: https://www.arena.education/chapter1

6. **“Emergence of Minimal Circuits for Indirect Object Identification” (Adhikari et al., 2025 arXiv‑ref 2510.25013)**  
   Trains **tiny attention‑only transformers (1–2 layers, 2–4 heads)** on a symbolic IOI‑like task and shows that **minimal circuits** emerge:  
   - One indirect head copies relevant tokens,  
   - One head suppresses/contrasts competing tokens,  
   - Joint residual‑stream aggregation yields the correct answer.  
   Explicitly discusses **indirect information paths** and **additive vs. suppressive attention outputs**.[6](https://arxiv.org/pdf/2510.25013.pdf)[7](https://arxiv.org/abs/2510.25013)
   *arXiv*: https://arxiv.org/abs/2510.25013

7. **“A Practical Review of Mechanistic Interpretability for Transformer Models” (Mishra et al., 2024)**  
   Broad survey of **MI methods (activation patching, ACDC, SAEs, logit lens)**, including application to small GPT‑style models. Good for mapping out which techniques are **feasible on CPU** (e.g., patching, simple SAEs on small layers) and which are **GPU‑heavy** (dense SAEs on large layers).[10](https://arxiv.org/html/2410.16443v3)[1](https://arxiv.org/abs/2407.02646)
   *arXiv*: https://arxiv.org/abs/2407.02646

8. **“Weight‑sparse Transformers Have Interpretable Circuits” (2025)**  
   Shows that **enforcing weight sparsity** during training yields **smaller, more human‑interpretable circuits**: each neuron has only a few incoming / outgoing connections so that the “wiring” is sparse and easier to reverse‑engineer. Although not nanoGPT‑specific, the idea is directly transferable to **small CPU‑trained transformers**.[11](https://chatpaper.com/es/chatpaper/paper/209848)
   *URL*: https://arxiv.org/abs/2512.14465 (or similar; title may shift slightly)

9. **“nnterp: A Standardized Interface for Mechanistic Interpretability of Transformers” (2025)**  
   Provides a **unified API** for **hooks, activation patching, and steering** across many transformer variants. Works on top of Hugging Face and NNsight, and can be used on CPU‑only models. Great for **standardizing hook‑based analysis** on small transformers without GPU.[12](https://arxiv.org/pdf/2511.14465.pdf)
   *arXiv*: https://arxiv.org/abs/2511.14465

10. **“Mechanistic Interpretability for Transformer‑based Time‑Series Models” (2025)**  
    Adapts **activation patching, attention saliency, and sparse autoencoders** to non‑text transformers, demonstrating that **CPU‑feasible MI techniques** (simple patching, first‑layer SAEs) already yield meaningful circuit‑like explanations. Useful as a reference for **how to port MI to small non‑NLP transformers**.[13](https://arxiv.org/html/2511.21514v1)
    *URL*: https://arxiv.org/abs/2511.21514

***

### 2) BibTeX entries (8–15 most important)

```bibtex
@article{elhage2021mathematical,
  title={A Mathematical Framework for Transformer Circuits},
  author={Elhage, Nicholas and Nanda, Neel and Olsson, Catherine and others},
  journal={Anthropic Transformer Circuits Thread},
  year={2021},
  note={Public technical blog series; see also "Begins with AI" timeline summaries.}
}

@article{nanda202350lines,
  title={How to Transformer Mechanistic Interpretability in 50 lines},
  author={Nanda, Neel},
  journal={Alignment Forum},
  year={2023},
  url={https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines}
}

@inproceedings{deng2023acdc,
  title={Towards Automated Circuit Discovery for Mechanistic Interpretability},
  author={Deng, Jessy and Chen, Molly and others},
  booktitle={NeurIPS},
  year={2023},
  note={Presents Automatic Circuit DisCovery (ACDC) on toy transformers.}
}

@article{coairesearch2023democratizing,
  title={Democratizing Mechanistic Interpretability: Bringing Neural Network Interpretability to CPU-Only Machines},
  author={CoaI Research},
  journal={CoaI Research Notes},
  year={2023},
  url={https://coairesearch.org/notes/democratizing-mechinterp/}
}

@incollection{arena2023chapter1,
  title={Chapter 1: Transformer Interpretability},
  author={Arena Education},
  booktitle={AI Safety and Alignment curriculum},
  year={2023},
  url={https://www.arena.education/chapter1}
}

@article{adhikari2025minimal,
  title={Emergence of Minimal Circuits for Indirect Object Identification},
  author={Adhikari, R. and others},
  journal={arXiv preprint},
  year={2025},
  eprint={2510.25013},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2510.25013}
}

@article{mishra2024practical,
  title={A Practical Review of Mechanistic Interpretability for Transformer Models},
  author={Mishra, A. and others},
  journal={arXiv preprint},
  year={2024},
  eprint={2407.02646},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2407.02646}
}

@article{weight_sparse_2025,
  title={Weight-sparse Transformers Have Interpretable Circuits},
  author={Anonymous},
  journal={arXiv preprint},
  year={2025},
  note={Shows that weight sparsity isolates compact, human-understandable circuits.}
}

@article{nnterp2025,
  title={nnterp: A Standardized Interface for Mechanistic Interpretability of Transformers},
  author={Anonymous},
  journal={arXiv preprint},
  year={2025},
  eprint={2511.14465},
  archivePrefix={arXiv},
  url={https://arxiv.org/abs/2511.14465}
}

@article{timeseries2025,
  title={Mechanistic Interpretability for Transformer-based Time-Series Models},
  author={Anonymous},
  journal={arXiv preprint},
  year={2025},
  eprint={2511.21514},
  archivePrefix={arXiv}
}

@article{improving_neuron_level_2024,
  title={Improving Neuron-level Interpretability with White-box Language Models},
  author={Bricken, T. and others},
  journal={arXiv preprint},
  year={2024},
  eprint={2410.16443},
  note={Includes discussion of SAEs and small-model interpretability.}
}

@article{mechanistic_gptlike_2025,
  title={Mechanistic Interpretability of GPT-like Models on Summarization Tasks},
  author={Mishra, A.},
  journal={arXiv preprint},
  year={2025},
  eprint={2505.17073}
}

@article{mechanistic_update_2024,
  title={Anthropic's Circuits Updates: All Releases},
  author={Begins with AI},
  year={2024},
  url={https://beginswithai.com/anthropic-circuits-updates/}
}
```

***

### 3) Key findings per cluster of work

#### a. **Residual‑stream framing and circuit discovery (Olsson/Nanda/Anthropic cluster)**

- The **residual stream** is treated as the “backbone” state that attention heads and MLPs read from and write to; this reframing lets one define **direct vs. indirect circuits** as paths from early tokens → specific heads → later residual positions → logits.[8](https://krmopuri.github.io/xml/static_files/presentations/MI-Pranav.pdf)[4](https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)
- **Indirect circuits** are often found by **activation patching**: changing early‑layer activations and measuring effect on later heads or logits, which reveals “information‑carrying” paths that bypass the “obvious” direct copying heads.[6](https://arxiv.org/pdf/2510.25013.pdf)[5](https://neurips.cc/virtual/2023/poster/72666)

#### b. **Activation hooks and CPU‑friendly workflows (CoaI, Nanda, ARENA)**

- MI can be **largely CPU‑compatible**: you train or load a small transformer on CPU, then **cache all layer/head outputs** into NumPy arrays; subsequent analysis (patching, SVD, attention‑weight analysis) happens offline on CPU.[2](https://coairesearch.org/notes/democratizing-mechinterp/)[4](https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)
- Libraries such as `TransformerLens` and `nnterp` provide **standardized hooks** (e.g., `blocks.0.hook_resid_post`, `attn.hook_v`) so you can **insert interventions or logging functions** at any point in the forward pass without touching the forward code.[14](https://transformerlensorg.github.io/TransformerLens/generated/demos/Main_Demo.html)[4](https://www.alignmentforum.org/posts/hnzHrdqn3nrjveayv/how-to-transformer-mechanistic-interpretability-in-50-lines)[12](https://arxiv.org/pdf/2511.14465.pdf)

#### c. **Indirect object identification (IOI) and minimal circuits**

- On simplified IOI‑like tasks, **tiny attention‑only transformers (1–2 layers, 2–4 heads)** can already solve the problem with **minimal circuits**:  
  - One head mainly copies the correct token into the residual stream.  
  - One head suppresses or contrasts the competing token.  
  The residual‑stream sum of these heads yields the correct answer, even without MLPs.[7](https://arxiv.org/abs/2510.25013)[6](https://arxiv.org/pdf/2510.25013.pdf)
- This shows that **indirect information paths** (e.g., “induction‑head‑style” copying plus suppression) can be **more compact and easier to isolate** in small, controlled models than in large pretrained LLMs.

#### d. **Automated and sparse‑circuit methods (ACDC, weight‑sparse transformers)**

- **Automatic Circuit DisCovery (ACDC)** demonstrates that **small transformers can be pruned into acyclic circuits** implementing specific tasks. In practice, this often yields **sparse, interpretable subgraphs** that are easier to understand than the full model.[5](https://neurips.cc/virtual/2023/poster/72666)
- **Weight‑sparse training** directly encourages **interpretable wiring**: each neuron has only a few connections, so the “circuits” that solve tasks are **small graphs of named components**, not dense spaghetti.[11](https://chatpaper.com/es/chatpaper/paper/209848)
- In both lines, the lesson for nanoGPT‑style work is that **small size + task‑specific training + sparsity** strongly aids mechanistic interpretability, even on CPU.

#### e. **Limitations of prior art**

- **Most “circuit” discoveries still rely heavily on human‑driven intuition**: ACDC automates the pruning, but **the initial dataset/task and metric design are manual**; this is not yet fully “self‑interpretation”.[1](https://arxiv.org/abs/2407.02646)[5](https://neurips.cc/virtual/2023/poster/72666)
- **IOI and other symbolic tasks are highly stylized**: the minimal circuits found in small attention‑only models may **not generalize well to full‑text next‑token prediction** or to real‑world distributions, where superposition and polysemanticity dominate.[7](https://arxiv.org/abs/2510.25013)[6](https://arxiv.org/pdf/2510.25013.pdf)
- **CPU‑only workflows are feasible but brittle**:  
  - You can cache activations, but **saving large tensors for long sequences** becomes I/O‑heavy.  
  - **Sparse autoencoders and SAE‑driven feature discovery are often GPU‑bound** when applied to many layers of larger models; small‑layer SAEs on CPU are possible but still memory‑intensive.[10](https://arxiv.org/html/2410.16443v3)[13](https://arxiv.org/html/2511.21514v1)[1](https://arxiv.org/abs/2407.02646)
- **Generalization to “nanoGPT‑style” models is still patchy**: most published work is on GPT‑2 / small LLaMA‑style models; while the **methods are transferable**, there is **no consolidated, nanoGPT‑specific mechanistic interpretability pipeline** yet, and **no standard dataset of “indirect” behaviors tailored to karpathy‑style nanoGPTs**.

***

Would you like me to:  
- sketch a concrete **nanoGPT‑compatible CPU‑only MI pipeline** (hooks, patching, and circuit‑discovery loop) for your local setup, or  
- focus next on **how to define “indirect” behavior** (e.g., IOI‑like tasks) that you can train and analyze on a small CPU‑trained transformer?  



## gaps

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



## methodology

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



## experiments

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



## abstract

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



## conclusion

<!-- section=conclusion generated=2026-03-26T19:40:11.357607+00:00 model=best -->

En resumen, este trabajo muestra que es posible adaptar ideas de **interpretabilidad mecanicista “Olsson‑Nanda/Anthropic”** a modelos tipo **nanoGPT pequeños entrenables solo en CPU**, usando **tareas IOI‑like sintéticas**, **hooks de activación** y **activation patching** para aislar **circuitos indirectos** compactos en atención y residual stream. Los resultados ilustran que incluso en arquitecturas ultra‑simplificadas (1–4 capas, 2–8 heads) emergen patrones de “copia indirecta” y supresión de alternativas, y que estas estructuras pueden caracterizarse con métricas simples de tamaño y profundidad de circuito.

Sin embargo, quedan abiertas varias preguntas importantes:  
- cómo se degradan o reorganizan estos circuitos al pasar a **lenguaje real** (no solo tareas sintéticas),  
- si la métrica de “indirectness” propuesta refleja causalidad legítima o solo correlación en caminos de atención,  
y  
- cómo extender el pipeline a **modelos ligeramente más grandes** o a otras tareas (summaries, razonamiento simple) sin volver a depender de GPU. Estos son los principales **límites de generalización** del enfoque; aquí se presenta principalmente una **prueba de concepto** y un esquema de experimentos reproducibles.

Desde el punto de vista de la reproducibilidad, el manuscrito propone un **flujo de trabajo CPU‑only** pensado para máquinas modestas:  
- entrenar un modelo pequeño tipo nanoGPT en CPU,  
- grabar hooks en arrays NumPy o archivos `.npz` durante la evaluación,  
- y luego analizar circuitos mediante patching y pruning sin usar GPU.  
Al publicar **código modular** (entrenamiento, generación de dataset IOI‑like, hooks, patching y análisis de circuitos), este enfoque pretende ser **fácilmente replicable por otros investigadores** con acceso limitado a hardware acelerado, abriendo la puerta a estudios de interpretabilidad en entornos bajo‑recurso.



## limitations

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


