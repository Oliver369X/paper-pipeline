<!-- section=gaps generated=2026-03-29T06:14:14.480009+00:00 model=best -->

Here are **open problems, methodological gaps, and underexplored settings** that are worth targeting for a submission that builds on arXiv:2510.24256. Each is phrased as a bullet with a one‑line rationale.

***

### Model‑class and architecture gaps

- Not yet tested on **3‑bit‑quantized LMs, MoE‑style LMs, or non‑Transformer sequence models (e.g., RNNs/TCNs)**, so the “spectrum” claim is still Transformer‑ and dense‑only.  
- No systematic analysis across **very small models (e.g., <200M)**, so it is unclear whether curvature‑based disentanglement collapses or changes at tiny scales.  
- The ViT trials are limited; the **generality of the spectrum to CNNs or hybrid architectures** is underexplored.  
- The method is applied to **MLP weights only**, leaving the role of attention‑weight curvature and head‑specific flatness vs sharptype directions largely unexplored.  

***

### Methodological and interpretability gaps

- The K‑FAC‑based editing is **“heavy‑handed” and global**; there is no structured pruning / channel‑wise or head‑wise rule that can approximate the same effect more efficiently.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- The **link between low‑curvature modes and specific mechanistic circuits** (e.g., MLP channels, attention heads, or residual streams) is only hinted at, not systematically mapped.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[4](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- The **dependence on curvature‑estimation dataset** (e.g., memorization‑heavy vs balanced subsets) is not systematically varied; it is unclear how robust the spectrum is to that choice.[2](https://arxiv.org/html/2510.24256v2)[5](https://arxiv.org/html/2510.24256v1)
- The paper uses **one scalar threshold $$\rho$$**; there is no study of how to **adaptively choose $$\rho$$ per layer or per task** to trade off memorization vs reasoning.[6](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v2)
- The method does **not exploit task‑specific labels**; the spectrum is inferred purely from curvature of the loss, so there is no explicit way to **align low‑curvature edits with a user‑defined “forget set” or privacy policy**.[7](https://arxiv.org/abs/2510.24256)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

***

### Training‑dynamics and data‑distribution gaps

- The effect of **fine‑tuning regimes** (e.g., continued pre‑training vs. multi‑task instruction‑tuning) on the curvature spectrum is not explored; it is unclear whether the spectrum shifts radically after SFT.[8](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- The role of **data quality / distribution shift** (e.g., noisy vs clean corpora, long‑tailed vs uniform) on the emergence of low‑curvature memorization‑like directions is underexplored.[9](https://proceedings.mlr.press/v235/garg24a.html)[10](https://raw.githubusercontent.com/mlresearch/v235/main/assets/garg24a/garg24a.pdf)
- The method is evaluated on **static checkpoints**, not on **continual‑learning or streaming settings**, so it is unclear how the spectrum evolves as a model is updated online.[2](https://arxiv.org/html/2510.24256v2)[8](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### Task‑and safety‑relevant gaps (for a follow‑up paper)

- The paper identifies **fact retrieval and arithmetic as “memorization‑like” brittle tasks**, but does not propose **fine‑tuning or re‑teaching strategies** to recover those skills after editing.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- There is **no explicit connection to safety‑critical behaviors** (e.g., hallucination, bias, privacy leakage); it is not shown how curvature‑based editing affects these, even though the method is motivated in part as a privacy‑oriented unlearning tool.[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- The **robustness of the spectrum under adversarial prompts or distributionally shifted inputs** (e.g., paraphrases, code‑switching, or synthetic attacks) is not tested.[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### Practical deployment and scalability gaps

- The **K‑FAC covariance pass is expensive** even for medium‑scale models; there is no lightweight proxy (e.g., low‑rank or random‑projection‑based) that can approximate the curvature spectrum cheaply.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- No **end‑to‑end pipeline** is provided for integrating curvature‑based editing as a **production‑ready unlearning or privacy‑mitigation step**, so the practical deployability is unclear.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)
- The **trade‑off Pareto front** between memorization removal, generalization, and reasoning is not explicitly mapped across multiple baselines (e.g., K‑FAC vs SVD vs BSN), leaving the “best” operating point underspecified.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

If you tell me whether you want to chase **a “mechanistic‑interpretability” story**, **a “practical unlearning / privacy” angle**, or **a “scaling‑laws / generalization” angle**, I can narrow this list into a concrete 1–2 “axes” for your paper targeting arXiv:2510.24256.
