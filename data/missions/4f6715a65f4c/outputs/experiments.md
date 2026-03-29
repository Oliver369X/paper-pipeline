<!-- section=experiments generated=2026-03-29T06:13:52.964643+00:00 model=best -->

Below is a compact, concrete **experiment plan** for replicating *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256), with suggested baselines, metrics, ablations, computational‑budget notes, and a Markdown‑ready results table.

***

### 1. Baselines

Run these editing methods on the same model(s) and data splits:

1. **K‑FAC editing (Paper method)**[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
   - K‑FAC decomposition of MLP weights $$W \approx G \otimes A$$, sort modes by $$\Pi_{ij}=\lambda_i\mu_j$$, keep top curvature‑mass fraction $$\rho$$ (≈0.6–0.9).  
2. **BalancedSubnet (BSN) – supervised unlearning**[2](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/abs/2510.24256)
   - Supervised “unlearning” baseline that squeezes memorization‑specific behavior into a small subnet.  
3. **SVD‑based editing (Rank‑truncation)**[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
   - Same MLPs, but truncate by singular values instead of curvature‑ordered modes.  
4. **Random‑direction editing (Null)**  
   - Same number of directions masked, but chosen uniformly at random in the K‑FAC basis.  
5. **Van‑3D / no‑edit (Control)**  
   - Untouched base model, plus optionally a standard fine‑tune on the same data.

***

### 2. Metrics

Measure these per method and dataset:

- **Memorization & Recitation:**  
  - Exact‑match accuracy on:  
    - Targeted memorized data (e.g., noised‑label or “quote‑style” splits).  
    - Untargeted memorized data (e.g., held‑out “memorized‑quotes” or Dolma‑style memorized sentences).[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - Perplexity on:  
    - Clean test data (to measure generalization).  
    - “Memorization‑hot” data (to measure how much narrow overfitting is removed).[2](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/abs/2510.24256)

- **Reasoning & Generalization:**  
  - Arithmetic (GSM8K‑style): accuracy and error types (e.g., reasoning vs arithmetic).[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - Closed‑book fact retrieval: QA accuracy on held‑out facts.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)
  - Open‑book fact retrieval: QA with retrieval‑augmented prompts (to test robustness).[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)
  - Logical reasoning (e.g., non‑numerical CRT‑style tasks): accuracy and “chain‑quality” measures.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

- **Curvature‑specific metrics:**  
  - Average activation strength of each task’s data on low‑curvature components (K‑FAC modes with $$\Pi_{ij}$$ in the lowest 20–30%).[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - Correlation between that activation strength and the **relative drop in performance** post‑editing.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

***

### 3. Ablations

Key ablations to run on **one main model** (e.g., an LM ≈2–7B):

1. **Editing fraction $$\rho$$**  
   - Sweep $$\rho \in \{0.5, 0.7, 0.8, 0.9, 1.0\}$$ for K‑FAC and SVD.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
   - Track: recitation reduction, perplexity, arithmetic / fact‑retrieval drop.

2. **Layer‑wise vs global editing**  
   - *Global:* same $$\rho$$ for all MLPs.  
   - *Layer‑wise:* smaller $$\rho$$ for early MLPs, larger for late MLPs (or vice versa).[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

3. **Curvature vs SVD ordering**  
   - For each $$\rho$$, compare K‑FAC‑ordered vs SVD‑ordered modes.[4](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

4. **Data‑scale for K‑FAC estimation**  
   - Small batch (≈1k–5k) vs large batch (≈50k–100k) for estimating $$A$$ and $$G$$.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

5. **Random‑seed sensitivity**  
   - 3–5 seeds per method, reporting mean ± std on key metrics.

***

### 4. Computational budget considerations

Assume you want to keep this on **one GPU node (e.g., 1–4 A100s / H100s)**:

- **Model choice:**  
  - Prefer a **smaller LLM** (e.g., OLMo‑2‑1B/2B or a 2–3B Llama‑style model) instead of 7B+ for cheaper K‑FAC passes and faster iteration.[6](https://rosinality.substack.com/p/2026-01-26)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - ViT can be omitted initially; focus on LM replication first.

- **K‑FAC pass cost:**  
  - One full K‑FAC pass ≈ 1–3× a normal forward‑backward pass over the curvature‑estimation dataset.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - Use **micro‑batching** (e.g., 1–2 small GPUs per host) and **checkpointing** to avoid OOM when computing $$A$$ and $$G$$.

- **Memory‑vs‑time trade‑off:**  
  - For iteration speed, run on a **smaller dataset slice** (e.g., 10k–50k samples) for K‑FAC and then validate on a larger test set.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - If budget allows, scale up the curvature‑estimation dataset for a final “scaling” experiment.

- **Editing is cheap:**  
  - The actual weight‑editing (matrix reconstruction in K‑FAC basis) is **one‑time linear‑algebra** per layer and can run on a CPU.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

***

### 5. Suggested results table outline (Markdown)

You can use this as a base table for your paper / report:

```markdown
| Model / Dataset                               | Method        | ρ (fraction kept) | Untargeted recitation ↓ | Targeted recitation ↓ | Perplexity Δ (%) | Arithmetic acc ↓ | Fact‑retrieval (CB) ↓ | Fact‑retrieval (OB) ↓ | Logical reasoning Δ |
|-----------------------------------------------|---------------|-------------------|--------------------------|------------------------|-------------------|------------------|------------------------|------------------------|---------------------|
| LLM‑2B (memorized‑text)                      | None          | 1.0               | 0.0                      | 0.0                    | 0.0               | 0.0              | 0.0                    | 0.0                    | 0.0                 |
| LLM‑2B (memorized‑text)                      | K‑FAC         | 0.5               | -78.3%                   | -92.1%                 | +1.2%             | -23.4%           | -18.7%                 | -2.1%                  | +3.5%               |
| LLM‑2B (memorized‑text)                      | K‑FAC         | 0.7               | -61.2%                   | -80.3%                 | +0.8%             | -12.1%           | -9.3%                  | -1.0%                  | +1.2%               |
| LLM‑2B (memorized‑text)                      | K‑FAC         | 0.9               | -29.1%                   | -45.7%                 | +0.3%             | -5.2%            | -3.8%                  | -0.5%                  | +0.4%               |
| LLM‑2B (memorized‑text)                      | SVD           | 0.5               | -50.1%                   | -68.4%                 | +3.1%             | -18.9%           | -15.2%                 | -4.3%                  | -2.1%               |
| LLM‑2B (memorized‑text)                      | SVD           | 0.7               | -32.7%                   | -49.6%                 | +1.9%             | -9.7%            | -8.1%                  | -2.2%                  | -1.0%               |
| LLM‑2B (memorized‑text)                      | Random‑K‑FAC  | 0.5               | -25.3%                   | -38.2%                 | +1.5%             | -6.4%            | -4.9%                  | -0.8%                  | +0.3%               |
| LLM‑2B (memorized‑text)                      | BSN (fine‑tune) | –              | -60.0%                   | -85.0%                 | +5.7%             | -21.3%           | -17.4%                 | -3.9%                  | -3.2%               |
| ... (additional ablations, e.g., layer‑wise) | ...           | ...               | ...                      | ...                    | ...               | ...              | ...                    | ...                    | ...                 |
```

- Add **correlation columns** (low‑curvature activation vs per‑task performance drop) in a separate table or appendix.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

***

If you tell me your **exact hardware** (e.g., “1× A100 80GB, 2× 40GB A100s”) and whether you want to prioritize **replication** or **an extension** (e.g., structured pruning, mechanistic mapping), I can turn this into a **week‑by‑week experiment plan** (e.g., “Week 1: K‑FAC infra; Week 2: baseline SVD/BSN; Week 3: systematic ρ‑sweep”). What scale of model are you targeting?
