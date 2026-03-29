<!-- section=limitations generated=2026-03-29T06:15:42.989779+00:00 model=best -->

Below is a **structured list of limitations and threats to validity** specifically for work that replicates or extends *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256), with an eye toward scope, synthetic vs. real data, interpretability claims, and hardware‑scale considerations.

***

### 1. Scope and model‑class limitations

- **Transformer‑only scope:** The method is validated only on transformers (LMs and ViTs); there is no evidence yet that the same curvature‑based spectrum holds for RNNs, CNNs, or MoE‑style models, so claims about “universal” memorization‑reasoning spectra are premature.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Narrow range of model sizes:** The original experiments use a small‑to‑medium transformer; the behavior of the spectrum under **large‑scale LMs (e.g., 13B+)** or **heavily quantized models** remains untested, which limits direct extrapolation to production‑scale systems.[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Limited training‑regime coverage:** The analysis is on standard autoregressive training; the curvature spectrum under **instruction‑tuning**, **RL‑based fine‑tuning**, or **continual‑learning** is not explored, so claims about stability of the spectrum over time are weak.[1](https://arxiv.org/abs/2510.24256)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### 2. Synthetic vs. real‑data limitations

- **Synthetic / controlled “memorized” data:** Many experiments use noised‑label or hand‑crafted “memorizable” splits, which may not capture the **complex, long‑tailed structure of real‑world memorization** (e.g., web‑scraped text, user‑specific data).[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[1](https://arxiv.org/abs/2510.24256)
- **Missing privacy‑relevant data regimes:** The paper does not test on realistic privacy‑sensitive corpora (e.g., PII‑heavy logs, code‑specific data), so it is unclear how well curvature‑based editing really removes **sensitive memorized content** versus benign overfitting.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Curvature‑estimation dataset bias:** The K‑FAC pass is computed on a subset of the training data; if that subset is skewed toward or away from memorized examples, the inferred curvature spectrum may not generalize to other data slices.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

***

### 3. Interpretability and causal‑claim threats

- **Correlation ≠ circuit semantics:** While the paper shows that low‑curvature directions correlate with memorization and certain tasks (e.g., arithmetic, closed‑book fact retrieval), it does **not prove** that these directions are *causally responsible* for those behaviors; the mapping to “circuits” remains largely correlational.[6](https://arxiv.org/html/2510.24256v1)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **“Memorization” vs “narrowly‑used” directions:** The low‑curvature directions may encode not just memorization but also other **narrow, task‑specific mechanisms** (e.g., math‑routines, fact‑compression); claiming that “low‑curvature = purely memorization” conflates memorization with specialization.[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Activation‑strength metric is coarse:** The activation‑strength projection of tasks onto low‑curvature modes is averaged over examples and does not distinguish whether only a **small fraction of inputs** drive the drop, so the interpretability claim can be misleading at the instance level.[6](https://arxiv.org/html/2510.24256v1)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

### 4. Methodological and measurement‑related threats

- **K‑FAC is approximate:** The curvature decomposition relies on the K‑FAC approximation $$F_W \approx G \otimes A$$; the smallest eigendirections are numerically fragile, and the “low‑curvature” tail may be contaminated by estimation noise rather than meaningful structure.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[4](https://proceedings.mlr.press/v235/ravikumar24a.html)
- **Editing is heavy‑handed:** The method removes entire low‑curvature subspaces at once; this global change makes it hard to isolate whether effects are due to **true memorization removal** or to **general weight‑decay‑like degradation** of specialized skills.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Evaluation metrics are proxy‑based:** The reliance on memorization‑benchmarks (e.g., quote‑recitation, noised‑label splits) and task‑specific accuracy (e.g., GSM8K‑style arithmetic) are useful proxies, but they do not fully capture **real‑world robustness, hallucination, or safety‑related behaviors**.[7](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)

***

### 5. Replication and “arXiv‑2510.24256‑targeted” validity threats

- **Dependency on provided code and data splits:** If the replication is done on a slightly different data‑splitting scheme or random seed, the exact curvature‑ordering and performance deltas may shift, undermining direct comparison with the original numbers.[8](https://huggingface.co/papers/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Hardware‑induced numerical noise:** Lower‑precision K‑FAC passes (e.g., 16‑bit or 8‑bit when using consumer‑grade GPUs) can perturb the small‑eigenvalue tail, so the “low‑curvature” spectrum is not fully reproducible across hardware tiers without careful numerics.[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Incomplete mechanistic‑baseline coverage:** Many follow‑up studies (including your replication) will not compare to *all* prior memorization‑analysis tools (e.g., input‑curvature‑based measures, activation‑based membership‑inference metrics), so the “relative advantage” of curvature‑based editing may be overstated.[9](https://journals.sagepub.com/doi/pdf/10.1177/23328584241303495?download=true)[4](https://proceedings.mlr.press/v235/ravikumar24a.html)

***

### 6. What would require larger models or GPU‑heavy experiments

These points are **explicitly beyond small‑scale replication** and require substantial GPU or model‑scale investment:

- **Scaling the spectrum to 13B+ LMs or multimodal‑ViTs:** Computing full K‑FAC‑style passes over such models is **extremely GPU‑heavy**, and memory‑bandwidth typically becomes the limiting factor.[1](https://arxiv.org/abs/2510.24256)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Continual‑learning / streaming‑K‑FAC:** Continuously updating curvature estimates as the model is updated online would require **long‑Running K‑FAC pipelines** over evolving data streams, which is computationally prohibitive on small clusters.[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **High‑resolution circuit‑mapping scans:** Fine‑grained ablations (e.g., down to head‑ or channel‑level pruning patterns guided by curvature) across many layers would require **large‑scale ablation sweeps** that are infeasible without 4–8+ high‑end GPUs.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

If you tell me whether your paper is framed as a **strict replication** vs a **modest extension** (e.g., interpretability‑focused or safety‑oriented), I can help you distill this list into a 6–8‑sentence “Limitations” paragraph that fits naturally in your arXiv‑style paper.
