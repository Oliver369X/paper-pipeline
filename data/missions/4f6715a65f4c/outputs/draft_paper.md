

---

> **Replication status: DEGRADED** — replication_tier=planning_only — el benchmark integrado no valida recolección K-FAC ni réplica fiel del paper. Ver `capability_contract` en `outputs/metrics.json`.
> Ver `outputs/replication_status.md`, `outputs/metrics.json` y `outputs/experiment_diagnostics.json`.

# Draft: Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256)

**Target venue / reference:** arXiv:2510.24256

*Disclaimer: borrador asistido por LLM (Perplexity); no sustituye experimentos ejecutados, números reproducibles ni revisión por pares. Ver `docs/MODE_NARRATIVE_VS_EMPIRICAL.md` y `docs/ARXIV_TARGET_ALIGNMENT.md` en el repositorio.*

*Generated 2026-03-29T06:15:54.571022+00:00 UTC*

## methodology



Here is a **concrete, paper‑oriented methodology** for replicating and extending *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256) with a clear path toward publishing your own follow‑up at arXiv.

---

### 1. Problem formulation

**Primary replication goal:**  
Reimplement the core claim that **low‑curvature directions in the K‑FAC basis of MLP weights encode memorization‑heavy, “narrow” capabilities**, while **higher‑curvature directions support generalization and reasoning**, and that editing the low‑curvature subspace suppresses recitation without destroying robust reasoning.

**Extension target (for your own paper):**  

- **Refine or generalize the spectrum:** test whether the “memorization → reasoning” spectrum holds across *different model families* (e.g., 3‑bit‑quantized LMs, MoE‑style LMs, or RNN‑based LMs) or *different training dynamics* (fine‑tuning vs. continual learning).  
- **Make the procedure more practical or interpretable:**  
  - Propose a *lighter, faster* or *more modular* curvature‑based editing rule (e.g., layer‑wise thresholds, structured pruning patterns).  
  - Connect curvature‑based components to *mechanistic circuits* (e.g., attention heads, MLP‑channel patterns) rather than treating them as abstract directions.

In short, your problem statement can be:

> *“How can we systematically reproduce and generalize the curvature‑based disentanglement of memorization and reasoning in transformer models, and what do these curvature‑based components structurally correspond to in the model?”*

---

### 2. Baselines to compare against

For a convincing replication *and* a paper‑worthy extension, you should include at least the following baselines:

1. **Original K‑FAC editing (paper baseline):**
  - Re‑implement the K‑FAC decomposition of MLP weight matrices $$W$$ via activation‑gradient covariances $$G \otimes A$$.  
  - Compute curvature‑ordered components and perform the low‑curvature subspace removal (keep top fraction $$\rho$$ of curvature mass).[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
2. **BalancedSubnet (BSN):**
  - Re‑implement or wrap the supervised unlearning baseline used in the paper (targeted removal of memorized data with a subnet‑compression objective).[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
  - Compare on:  
    - recitation of targeted and *untargeted* memorized facts,  
    - perplexity on clean test data,  
    - robustness under stress tests (e.g., paraphrased or slightly perturbed inputs).
3. **SVD‑based editing (control):**
  - Same MLP‑weight editing, but using SVD rank‑truncation instead of curvature‑ordered components.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - This tests whether the *curvature* ordering is crucial, or if any low‑rank truncation produces similar effects.
4. **Random‑direction editing (null):**
  - Randomly zero out a comparable fraction of weight directions in the K‑FAC basis to check that the low‑curvature ones are *special* rather than just “whatever gets masked”.
5. **No‑editing / vanilla fine‑tuning (control):**
  - A standard fine‑tune or continued‑training regime on the same data to see if the same behavior can be achieved more clumsily.

---







- Choose **one or two LMs** (e.g., a small‑open‑weight LM such as OLMo‑2‑7B‑hf or a similarly sized Llama‑derived model) and **one ViT** (ImageNet‑style).[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- Use  
  - **Memorization probes:** curated datasets of quotes, facts, or synthetic “memorizable” items used in the paper.  
  - **Reasoning & fact‑retrieval benchmarks:** MMLU‑style reasoning, GSM8K‑style arithmetic, Fact‑Retrieval QA, and an “open‑book” variant (e.g., with retrieval‑augmented prompts).[3](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)



- 
  - activation covariance $$A = \mathbb{E}[aa^T]$$,  
  - gradient covariance $$G = \mathbb{E}[gg^T]$$.  
  - Form the approximate FIM block $$F_W \approx G \otimes A$$.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- 



- **Original K‑FAC method:**  
  - Keep the top curvature‑mass fraction $$\rho$$ (e.g., 0.7–0.9) and reconstruct the edited weight:  
  $$
  W_{\text{edit}} = U_G \bigl( (U_G^T W U_A) \odot M \bigr) U_A^T,
  $$
  where $$M_{ij}=1$$ if $$(i,j)\in S$$ (kept pairs) and 0 otherwise.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Your extension ideas (pick 1–2 to publish):**  
  - **Layer‑wise or task‑specific thresholds:** Allocate different $$\rho_\ell$$ per layer, or per probe task (e.g., larger $$\rho$$ for reasoning layers, smaller for shallow MLPs).  
  - **Structured pruning:** instead of full SVD‑style K‑FAC, mask only certain *channels* or *heads* correlated with low‑curvature modes.  
  - **Curvature‑aware fine‑tuning:** after editing, apply a light PPO‑ or DPO‑style tuning to recover specific skills (e.g., reasoning) while keeping memorization suppressed.





- **Memorization:**  
  - strict/loose accuracy on memorized quotes or facts (targeted and untargeted).[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - perplexity on held‑out memorized data vs. “clean” data.
- **Generalization & robustness:**  
  - validation perplexity on clean LM data / ViT top‑1 accuracy.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - stress‑test accuracy (e.g., paraphrased inputs, positional shifts).[3](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)
- **Reasoning spectrum:**  
  - drop in performance on:  
    - closed‑book fact retrieval,  
    - arithmetic (e.g., GSM8K‑style),  
    - open‑book QA,  
    - general logical reasoning (e.g., non‑numerical CRT‑style tasks).
  - correlate each task’s activation strength along low‑curvature components with its post‑edit performance drop.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)



- **Activation projection:** for each task’s input, project the internal representations (e.g., final‑layer MLP outputs) onto the K‑FAC basis and report how much energy lies in low‑ vs. high‑curvature modes.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Circuit mapping:**  
  - Tie low‑curvature components to specific attention heads or MLP channels, e.g., by checking which heads have the strongest correlation with low‑curvature directions.  
  - Perform **sparse pruning** experiments: remove only the top‑10% heads/channels most correlated with low‑curvature modes and compare with K‑FAC‑based editing.

---





- ✅ **Clean replication** of the main curve:  
  - Demonstrate that K‑FAC editing:  
    - suppresses recitation of *both* targeted and *untargeted* memorized data more effectively than BSN while keeping perplexity lower or similar.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
    - selectively hurts arithmetic and closed‑book fact retrieval, while open‑book and general reasoning are conserved or slightly improved.[3](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- ✅ **Interpretive extension:**  
  - Show that the *activation strength* of a task’s data on the low‑curvature subspace strongly correlates with its *performance drop* after editing (Figure‑quality quantitative plot).[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- ✅ **One clear “new” contribution:**  
  - At least *one* of the following:  
    - A **lighter / more modular curvature‑based editing rule** (e.g., structured pruning, layer‑wise thresholds) that matches or beats the original K‑FAC method on a subset of metrics.  
    - A **mechanistic story**: show that low‑curvature directions are spatially concentrated in certain attention heads or MLP channels, and that pruning those is a viable alternative to K‑FAC editing.[4](https://www.linkedin.com/posts/charlesmartin14_%F0%9D%97%99%F0%9D%97%BF%F0%9D%97%BC%F0%9D%97%BA-%F0%9D%97%A0%F0%9D%97%B2%F0%9D%97%BA%F0%9D%97%BC%F0%9D%97%BF%F0%9D%97%B6%F0%9D%98%87%F0%9D%97%AE%F0%9D%98%81%F0%9D%97%B6%F0%9D%97%BC%F0%9D%97%BB-%F0%9D%98%81%F0%9D%97%BC-activity-7392365987003744256-LuAU)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)



- Replicates the core insight of *“memorization lives in low‑curvature directions, reasoning in higher‑curvature”*.  
- Proposes a concrete, implementable editing or pruning rule.  
- Adds mechanistic or interpretability insight (e.g., “which heads are memorization‑heavy”).

---



&nbsp;





&nbsp;

---





1. **K‑FAC editing (Paper method)**[123](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - K‑FAC decomposition of MLP weights $$W \approx G \otimes A$$, sort modes by $$\Pi_{ij}=\lambda_i\mu_j$$, keep top curvature‑mass fraction $$\rho$$ (≈0.6–0.9).
2. **BalancedSubnet (BSN) – supervised unlearning**[21](https://arxiv.org/abs/2510.24256)
  - Supervised “unlearning” baseline that squeezes memorization‑specific behavior into a small subnet.
3. **SVD‑based editing (Rank‑truncation)**[341](https://arxiv.org/abs/2510.24256)
  - Same MLPs, but truncate by singular values instead of curvature‑ordered modes.
4. **Random‑direction editing (Null)**
  - Same number of directions masked, but chosen uniformly at random in the K‑FAC basis.
5. **Van‑3D / no‑edit (Control)**
  - Untouched base model, plus optionally a standard fine‑tune on the same data.

---





- 
  - Exact‑match accuracy on:  
    - Targeted memorized data (e.g., noised‑label or “quote‑style” splits).  
    - Untargeted memorized data (e.g., held‑out “memorized‑quotes” or Dolma‑style memorized sentences).[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - Perplexity on:  
    - Clean test data (to measure generalization).  
    - “Memorization‑hot” data (to measure how much narrow overfitting is removed).[2](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/abs/2510.24256)
- 
  - Arithmetic (GSM8K‑style): accuracy and error types (e.g., reasoning vs arithmetic).[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - Closed‑book fact retrieval: QA accuracy on held‑out facts.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)
  - Open‑book fact retrieval: QA with retrieval‑augmented prompts (to test robustness).[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)
  - Logical reasoning (e.g., non‑numerical CRT‑style tasks): accuracy and “chain‑quality” measures.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- 
  - Average activation strength of each task’s data on low‑curvature components (K‑FAC modes with $$\Pi_{ij}$$ in the lowest 20–30%).[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - Correlation between that activation strength and the **relative drop in performance** post‑editing.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

---





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

---





- 
  - Prefer a **smaller LLM** (e.g., OLMo‑2‑1B/2B or a 2–3B Llama‑style model) instead of 7B+ for cheaper K‑FAC passes and faster iteration.[6](https://rosinality.substack.com/p/2026-01-26)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - ViT can be omitted initially; focus on LM replication first.
- 
  - One full K‑FAC pass ≈ 1–3× a normal forward‑backward pass over the curvature‑estimation dataset.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
  - Use **micro‑batching** (e.g., 1–2 small GPUs per host) and **checkpointing** to avoid OOM when computing $$A$$ and $$G$$.
- 
  - For iteration speed, run on a **smaller dataset slice** (e.g., 10k–50k samples) for K‑FAC and then validate on a larger test set.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
  - If budget allows, scale up the curvature‑estimation dataset for a final “scaling” experiment.
- 
  - The actual weight‑editing (matrix reconstruction in K‑FAC basis) is **one‑time linear‑algebra** per layer and can run on a CPU.[3](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)

---





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

---



&nbsp;





&nbsp;

---



- Not yet tested on **3‑bit‑quantized LMs, MoE‑style LMs, or non‑Transformer sequence models (e.g., RNNs/TCNs)**, so the “spectrum” claim is still Transformer‑ and dense‑only.  
- No systematic analysis across **very small models (e.g., <200M)**, so it is unclear whether curvature‑based disentanglement collapses or changes at tiny scales.  
- The ViT trials are limited; the **generality of the spectrum to CNNs or hybrid architectures** is underexplored.  
- The method is applied to **MLP weights only**, leaving the role of attention‑weight curvature and head‑specific flatness vs sharptype directions largely unexplored.

---



- The K‑FAC‑based editing is **“heavy‑handed” and global**; there is no structured pruning / channel‑wise or head‑wise rule that can approximate the same effect more efficiently.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- The **link between low‑curvature modes and specific mechanistic circuits** (e.g., MLP channels, attention heads, or residual streams) is only hinted at, not systematically mapped.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[4](https://www.themoonlight.io/ko/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- The **dependence on curvature‑estimation dataset** (e.g., memorization‑heavy vs balanced subsets) is not systematically varied; it is unclear how robust the spectrum is to that choice.[2](https://arxiv.org/html/2510.24256v2)[5](https://arxiv.org/html/2510.24256v1)
- The paper uses **one scalar threshold $$\rho$$**; there is no study of how to **adaptively choose $$\rho$$ per layer or per task** to trade off memorization vs reasoning.[6](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v2)
- The method does **not exploit task‑specific labels**; the spectrum is inferred purely from curvature of the loss, so there is no explicit way to **align low‑curvature edits with a user‑defined “forget set” or privacy policy**.[7](https://arxiv.org/abs/2510.24256)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

---



- The effect of **fine‑tuning regimes** (e.g., continued pre‑training vs. multi‑task instruction‑tuning) on the curvature spectrum is not explored; it is unclear whether the spectrum shifts radically after SFT.[8](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- The role of **data quality / distribution shift** (e.g., noisy vs clean corpora, long‑tailed vs uniform) on the emergence of low‑curvature memorization‑like directions is underexplored.[9](https://proceedings.mlr.press/v235/garg24a.html)[10](https://raw.githubusercontent.com/mlresearch/v235/main/assets/garg24a/garg24a.pdf)
- The method is evaluated on **static checkpoints**, not on **continual‑learning or streaming settings**, so it is unclear how the spectrum evolves as a model is updated online.[2](https://arxiv.org/html/2510.24256v2)[8](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



- The paper identifies **fact retrieval and arithmetic as “memorization‑like” brittle tasks**, but does not propose **fine‑tuning or re‑teaching strategies** to recover those skills after editing.[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- There is **no explicit connection to safety‑critical behaviors** (e.g., hallucination, bias, privacy leakage); it is not shown how curvature‑based editing affects these, even though the method is motivated in part as a privacy‑oriented unlearning tool.[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- The **robustness of the spectrum under adversarial prompts or distributionally shifted inputs** (e.g., paraphrases, code‑switching, or synthetic attacks) is not tested.[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



- The **K‑FAC covariance pass is expensive** even for medium‑scale models; there is no lightweight proxy (e.g., low‑rank or random‑projection‑based) that can approximate the curvature spectrum cheaply.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v2)
- No **end‑to‑end pipeline** is provided for integrating curvature‑based editing as a **production‑ready unlearning or privacy‑mitigation step**, so the practical deployability is unclear.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[11](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)
- The **trade‑off Pareto front** between memorization removal, generalization, and reasoning is not explicitly mapped across multiple baselines (e.g., K‑FAC vs SVD vs BSN), leaving the “best” operating point underspecified.[2](https://arxiv.org/html/2510.24256v2)[3](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



&nbsp;





&nbsp;

---

- 
- 
- 
- 
- 
- 

---



&nbsp;





&nbsp;

---





&nbsp;

&nbsp;

---





&nbsp;

&nbsp;

---





- 
- 
- 
- 
- 



&nbsp;





&nbsp;

---



- **Transformer‑only scope:** The method is validated only on transformers (LMs and ViTs); there is no evidence yet that the same curvature‑based spectrum holds for RNNs, CNNs, or MoE‑style models, so claims about “universal” memorization‑reasoning spectra are premature.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Narrow range of model sizes:** The original experiments use a small‑to‑medium transformer; the behavior of the spectrum under **large‑scale LMs (e.g., 13B+)** or **heavily quantized models** remains untested, which limits direct extrapolation to production‑scale systems.[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Limited training‑regime coverage:** The analysis is on standard autoregressive training; the curvature spectrum under **instruction‑tuning**, **RL‑based fine‑tuning**, or **continual‑learning** is not explored, so claims about stability of the spectrum over time are weak.[1](https://arxiv.org/abs/2510.24256)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



- **Synthetic / controlled “memorized” data:** Many experiments use noised‑label or hand‑crafted “memorizable” splits, which may not capture the **complex, long‑tailed structure of real‑world memorization** (e.g., web‑scraped text, user‑specific data).[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[1](https://arxiv.org/abs/2510.24256)
- **Missing privacy‑relevant data regimes:** The paper does not test on realistic privacy‑sensitive corpora (e.g., PII‑heavy logs, code‑specific data), so it is unclear how well curvature‑based editing really removes **sensitive memorized content** versus benign overfitting.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Curvature‑estimation dataset bias:** The K‑FAC pass is computed on a subset of the training data; if that subset is skewed toward or away from memorized examples, the inferred curvature spectrum may not generalize to other data slices.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)

---



- **Correlation ≠ circuit semantics:** While the paper shows that low‑curvature directions correlate with memorization and certain tasks (e.g., arithmetic, closed‑book fact retrieval), it does **not prove** that these directions are *causally responsible* for those behaviors; the mapping to “circuits” remains largely correlational.[6](https://arxiv.org/html/2510.24256v1)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **“Memorization” vs “narrowly‑used” directions:** The low‑curvature directions may encode not just memorization but also other **narrow, task‑specific mechanisms** (e.g., math‑routines, fact‑compression); claiming that “low‑curvature = purely memorization” conflates memorization with specialization.[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- **Activation‑strength metric is coarse:** The activation‑strength projection of tasks onto low‑curvature modes is averaged over examples and does not distinguish whether only a **small fraction of inputs** drive the drop, so the interpretability claim can be misleading at the instance level.[6](https://arxiv.org/html/2510.24256v1)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



- **K‑FAC is approximate:** The curvature decomposition relies on the K‑FAC approximation $$F_W \approx G \otimes A$$; the smallest eigendirections are numerically fragile, and the “low‑curvature” tail may be contaminated by estimation noise rather than meaningful structure.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[4](https://proceedings.mlr.press/v235/ravikumar24a.html)
- **Editing is heavy‑handed:** The method removes entire low‑curvature subspaces at once; this global change makes it hard to isolate whether effects are due to **true memorization removal** or to **general weight‑decay‑like degradation** of specialized skills.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Evaluation metrics are proxy‑based:** The reliance on memorization‑benchmarks (e.g., quote‑recitation, noised‑label splits) and task‑specific accuracy (e.g., GSM8K‑style arithmetic) are useful proxies, but they do not fully capture **real‑world robustness, hallucination, or safety‑related behaviors**.[7](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)

---



- **Dependency on provided code and data splits:** If the replication is done on a slightly different data‑splitting scheme or random seed, the exact curvature‑ordering and performance deltas may shift, undermining direct comparison with the original numbers.[8](https://huggingface.co/papers/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Hardware‑induced numerical noise:** Lower‑precision K‑FAC passes (e.g., 16‑bit or 8‑bit when using consumer‑grade GPUs) can perturb the small‑eigenvalue tail, so the “low‑curvature” spectrum is not fully reproducible across hardware tiers without careful numerics.[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Incomplete mechanistic‑baseline coverage:** Many follow‑up studies (including your replication) will not compare to *all* prior memorization‑analysis tools (e.g., input‑curvature‑based measures, activation‑based membership‑inference metrics), so the “relative advantage” of curvature‑based editing may be overstated.[9](https://journals.sagepub.com/doi/pdf/10.1177/23328584241303495?download=true)[4](https://proceedings.mlr.press/v235/ravikumar24a.html)

---





- **Scaling the spectrum to 13B+ LMs or multimodal‑ViTs:** Computing full K‑FAC‑style passes over such models is **extremely GPU‑heavy**, and memory‑bandwidth typically becomes the limiting factor.[1](https://arxiv.org/abs/2510.24256)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Continual‑learning / streaming‑K‑FAC:** Continuously updating curvature estimates as the model is updated online would require **long‑Running K‑FAC pipelines** over evolving data streams, which is computationally prohibitive on small clusters.[4](https://proceedings.mlr.press/v235/ravikumar24a.html)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **High‑resolution circuit‑mapping scans:** Fine‑grained ablations (e.g., down to head‑ or channel‑level pruning patterns guided by curvature) across many layers would require **large‑scale ablation sweeps** that are infeasible without 4–8+ high‑end GPUs.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[3](https://mail.bycloud.ai/p/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

---



&nbsp;





&nbsp;

&nbsp;

&nbsp;