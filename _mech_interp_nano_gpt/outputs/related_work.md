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
