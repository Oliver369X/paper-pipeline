<!-- section=methodology generated=2026-03-29T06:13:16.481598+00:00 model=best -->

Here is a **concrete, paper‑oriented methodology** for replicating and extending *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256) with a clear path toward publishing your own follow‑up at arXiv.

***

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

***

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

***

### 3. Proposed method outline

You can structure your own method as a **replication + extension** pipeline:

#### A. Model and data setup
- Choose **one or two LMs** (e.g., a small‑open‑weight LM such as OLMo‑2‑7B‑hf or a similarly sized Llama‑derived model) and **one ViT** (ImageNet‑style).[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)[1](https://arxiv.org/abs/2510.24256)
- Use  
  - **Memorization probes:** curated datasets of quotes, facts, or synthetic “memorizable” items used in the paper.  
  - **Reasoning & fact‑retrieval benchmarks:** MMLU‑style reasoning, GSM8K‑style arithmetic, Fact‑Retrieval QA, and an “open‑book” variant (e.g., with retrieval‑augmented prompts).[3](https://techxplore.com/news/2025-11-ai-brain-reveals-memory.html)[1](https://arxiv.org/abs/2510.24256)

#### B. Curvature collection (K‑FAC style)
- Run a forward‑backward pass over a **representative slice of training / validation data** and collect for each MLP weight matrix $$W$$:  
  - activation covariance $$A = \mathbb{E}[aa^T]$$,  
  - gradient covariance $$G = \mathbb{E}[gg^T]$$.  
  - Form the approximate FIM block $$F_W \approx G \otimes A$$.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

- Compute the “curvature mass” for each mode pair $$(i,j)$$ as $$\Pi_{ij} = \lambda_i^\text{(G)} \mu_j^\text{(A)}$$, then order the modes by $$\Pi_{ij}$$ descending.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)

#### C. Weight editing
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

#### D. Quantitative metrics
For each method and baseline, measure:

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

#### E. Mechanistic / interpretability analysis (paper‑worthy extension)
- **Activation projection:** for each task’s input, project the internal representations (e.g., final‑layer MLP outputs) onto the K‑FAC basis and report how much energy lies in low‑ vs. high‑curvature modes.[1](https://arxiv.org/abs/2510.24256)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Circuit mapping:**  
  - Tie low‑curvature components to specific attention heads or MLP channels, e.g., by checking which heads have the strongest correlation with low‑curvature directions.  
  - Perform **sparse pruning** experiments: remove only the top‑10% heads/channels most correlated with low‑curvature modes and compare with K‑FAC‑based editing.

***

### 4. Minimal viable result (MVR) for a paper‑worthy project

A **minimal viable result** that already justifies an arXiv‑style paper could be:

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

If you can achieve this MVR on a **single but reasonably sized LM** (e.g., 2–7B parameters) and a **small ViT** (or just LM), you already have a solid arXiv‑style paper that:

- Replicates the core insight of *“memorization lives in low‑curvature directions, reasoning in higher‑curvature”*.  
- Proposes a concrete, implementable editing or pruning rule.  
- Adds mechanistic or interpretability insight (e.g., “which heads are memorization‑heavy”).

***

If you tell me which model sizes and hardware you have access to (e.g., “I can run 2‑bit‑quantized 7B on one A100” vs “only 1B–2B in 16‑bit”), I can sketch an even more concrete **per‑week experimental plan** (e.g., “Week 1: K‑FAC infra; Week 2: strict replication; Week 3: structured pruning + paper‑style plots”). What scale of model are you planning to run on?
