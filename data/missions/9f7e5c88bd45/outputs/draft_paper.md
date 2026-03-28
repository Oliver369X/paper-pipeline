# Draft: Curvatura de Pérdida K-FAC para la Mitigación de Memorización en SLMs

**Target venue / reference:** arXiv:2510.24256

*Disclaimer: borrador asistido por LLM (Perplexity); no sustituye experimentos ejecutados, números reproducibles ni revisión por pares. Ver `docs/MODE_NARRATIVE_VS_EMPIRICAL.md` y `docs/ARXIV_TARGET_ALIGNMENT.md` en el repositorio.*

*Generated 2026-03-27T19:16:25.505411+00:00 UTC*

## methodology



**K-FAC-based curvature editing offers a promising, data-efficient way to reduce memorization in small language models (SLMs) by targeting low-curvature directions in the loss landscape, extending ideas from arXiv:2510.24256 to resource-constrained settings.**[12](https://arxiv.org/pdf/2510.24256.pdf)

This methodology adapts the paper's K-FAC decomposition to SLMs like Phi-3-mini (3.8B parameters), focusing on feasibility for your AI safety research at YAIS Lab.[34](https://encord.com/blog/microsoft-phi-3-small-language-model/)

## Problem Formulation

Memorization in SLMs occurs when models regurgitate training sequences verbatim, quantified by prefix-suffix exact match under greedy decoding: for prompt $$P$$ and target $$S$$, compute Levenshtein distance $$d(\hat{S}, S)$$ where $$\hat{S}$$ is generated output.[25](https://mansisak.com/memorization/)

High per-example loss curvature links to brittle memorization, but aggregate dataset curvature reveals low-curvature directions (flatter basins) correspond to rarely used, memorization-heavy weights.[2](https://arxiv.org/pdf/2510.24256.pdf)

Objective: Decompose MLP weights via K-FAC-approximated Fisher Information Matrix (FIM) $$\mathbf{F} \approx \mathbf{G} \otimes \mathbf{A}$$, where $$\mathbf{G} = \mathbb{E}[\mathbf{g}\mathbf{g}^\top]$$ (gradients) and $$\mathbf{A} = \mathbb{E}[\mathbf{a}\mathbf{a}^\top]$$ (activations), then prune low-curvature components to suppress recitation while preserving perplexity and reasoning.[62](https://arxiv.org/pdf/2510.24256.pdf)

## Baselines

Compare against three classes from memorization mitigation literature, scaled to SLMs:[57](https://arxiv.org/html/2410.02159)

Use SVD truncation (prune low singular values) as data-free ablation.[2](https://arxiv.org/pdf/2510.24256.pdf)

## Proposed Method Outline

1. **Collect Statistics**: Stream ~1-5M tokens from SLM pretraining mix (e.g., FineMath + Dolma subset) through target SLM (Phi-3-mini). Buffer pre-MLP activations $$\mathbf{a}$$ (forward) and gradients $$\mathbf{g}$$ (backward under NLL). Compute $$\mathbf{A}, \mathbf{G}$$ per MLP layer.[32](https://arxiv.org/pdf/2510.24256.pdf)
2. **K-FAC Decomposition**: Eigendecompose $$\mathbf{G} = U_G \Lambda_G U_G^\top$$, $$\mathbf{A} = U_A \Lambda_A U_A^\top$$. For weight $$W \in \mathbb{R}^{p \times q}$$, project $$C = U_G^\top W U_A$$, sort pairs $$(i,j)$$ by curvature mass $$\Pi_{ij} = \lambda_i^G \mu_j^A$$. Retain top-$$\rho=60$$ mass pairs via mask $$M$$, reconstruct $$W' = U_G (C \odot M) U_A^\top$$.[62](https://arxiv.org/pdf/2510.24256.pdf)
3. **Edit & Tune**: Apply to late MLP layers (e.g., 80% from end, as in OLMo edits). Sweep $$\rho$$, layers (0.1% compute via small labeled forget set). No retraining needed, unlike BSN.[2](https://arxiv.org/pdf/2510.24256.pdf)
4. **Evaluation**: Test on held-out memorized sequences (e.g., Dolma val, quotes), compute strict/loose accuracy, avg. Levenshtein. Track perplexity, MMLU-Pro Math, logic (e.g., Boar Etruscan).[2](https://arxiv.org/pdf/2510.24256.pdf)







&nbsp;

&nbsp;

&nbsp;





&nbsp;







- **No intervention**: Untuned SLM as baseline for memorization levels.[4](https://arxiv.org/html/2510.24256v2)
- **SVD pruning**: Singular value decomposition on weights, retaining top components by magnitude.[4](https://arxiv.org/html/2510.24256v2)
- **Balanced Subnet (BSN)**: Supervised unlearning baseline that balances forget/retain sets.[4](https://arxiv.org/html/2510.24256v2)
- **Standard regularization**: Weight decay or dropout during fine-tuning.[8](https://arxiv.org/abs/1602.01407)







- Vary energy threshold (40%, 60%, 80% retained curvature mass) to balance forget/utility trade-off.[5](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)
- Target layers (last 1 vs. 2-3 MLPs) and projections (gate_proj only vs. up_proj).[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- Importance formula: Original (λ_i * μ_j) vs. modified (λ_i * μ_j * |C_ij|^2).[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- Dataset duplication factor (1x, 10x, 100x) to scale memorization induction.[11](https://floriantramer.com/publications/scaling22/)











- **Application to SLMs (<1B parameters):** arXiv:2510.24256 focuses on 1B-7B OLMo models; underexplored in resource-constrained SLMs where compute for K-FAC covariances may exceed training budgets, limiting feasibility for edge deployment.[1](https://arxiv.org/html/2510.24256v2)
- **Numerical stability for small eigenvalues:** Estimating low-curvature directions in SLMs risks instability due to noisy gradients in limited data regimes, unaddressed in the paper's larger-model sweeps.[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
- **Post-editing fine-tuning dynamics:** Paper notes potential need for further training after edits to regain expressivity, but gaps in SLM-specific strategies to prevent memorization resurgence during adaptation.
- **Beyond MLP edits to attention layers:** Method targets MLPs; underexplored extension to attention mechanisms, critical for memorization in SLMs with sparser activations.
- **Low-resource data settings:** Bulk data assumption for covariance collection doesn't hold for domain-specific SLMs (e.g., medical, code); no analysis of curvature signals in small/fine-tuned corpora.[3](https://www.nature.com/articles/s41746-025-01653-8)
- **Interaction with quantization/distillation:** No evaluation of K-FAC robustness under 4/8-bit quantization or distillation common in SLMs, where curvature approximations may degrade.[4](https://www.emergentmind.com/topics/kronecker-factored-approximate-curvature-k-fac-cfb12415-7bdc-42ec-b0f2-bb04c447624a)
- **Task-specific brittleness in SLMs:** Arithmetic/fact recall drops observed in LMs; open whether SLMs show similar spectrum or if reasoning is uniformly robust due to scale limits.
- **Theoretical guarantees for aggregate curvature:** Empirical inversion (low aggregate curvature = memorization) lacks proofs for SLMs, where double descent alters loss landscapes.







&nbsp;







- Dolma validation: Prefixed training sequences (64-token prefix, 48-token suffix) for targeted memorization.[1](https://arxiv.org/html/2510.24256v2)
- Historical Quotes: Out-of-distribution memorized quotes (8-token suffix) testing untargeted suppression.[1](https://arxiv.org/html/2510.24256v2)
- Pile10k: Clean text for perplexity.[1](https://arxiv.org/html/2510.24256v2)



- Strict Accuracy (%): Exact match of generated suffix (lower better for suppression).[1](https://arxiv.org/html/2510.24256v2)
- Loose Accuracy (%): ≥75% token overlap (lower better).[1](https://arxiv.org/html/2510.24256v2)
- Avg Normalized Levenshtein Distance (higher better, ~0-1).[1](https://arxiv.org/html/2510.24256v2)
- Perplexity (PPL, lower better for utility preservation).[1](https://arxiv.org/html/2510.24256v2)









&nbsp;

















&nbsp;

&nbsp;





&nbsp;







- **tensorflow/kfac**: https://github.com/tensorflow/kfac – Apache 2.0; last major 2018; K-FAC optimizer for TensorFlow, foundational for Hessian/curvature approx.[6](https://github.com/tensorflow/kfac)
- **google-deepmind/kfac-jax**: https://github.com/google-deepmind/kfac-jax – Apache 2.0; 2022; JAX library for scalable curvature and second-order optimization in NNs.[7](https://github.com/google-deepmind/kfac-jax)



&nbsp;





&nbsp;

&nbsp;

---



- The method targets **verbatim recitation of training‑set text** (e.g., quotes) and “shared” memorization patterns linked to low‑curvature directions in MLP weight matrices, but it does not claim to remove all forms of memorization (e.g., partial fragments, paraphrased content, or indirect leakage via reasoning‑like chains).[2](https://arxiv.org/html/2510.24256v1)[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[4](https://news.ycombinator.com/item?id=45845800)
- Empirical validation is mainly on **moderate‑size decoder‑only LMs** (LLaMA‑scale and similar); generalizing to much smaller or structurally different SLMs (e.g., very small RNNs, encoder‑decoder models, or non‑Transformer SLMs) may require re‑tuning and can invalidate the assumption that low‑curvature MLP directions systematically encode memorization.[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[5](https://news.ycombinator.com/item?id=45845835)[2](https://arxiv.org/html/2510.24256v1)

---



- Evaluation relies on **constructed “memorization” datasets** (e.g., curated quotes, card‑sort‑style evaluation, and synthetic benchmarks) rather than a broad slice of real‑world user‑generated text, which introduces a **construct‑validity threat**: the method may appear more effective on “clean” examples than on messy, noisy, or partially memorized text in practice.[4](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v1)[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- The **“unseen quotes”** test set is artificial/curated rather than a random sample of real‑world sensitive text; generalization to arbitrary PII, code, or proprietary text is thus not fully established, and performance may degrade on distribution‑shifted real‑world data.[2](https://arxiv.org/html/2510.24256v1)[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

---



- The work interprets **low‑curvature K‑FAC directions as “memorization‑prone”** and higher‑curvature directions as “reasoning‑like,” but this is **correlational and model‑specific**; there is no formal proof that curvature alone cleanly separates memorization from generalization mechanisms.[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[4](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v1)
- Interpretability claims (e.g., “pure memorization on one end, logical reasoning on the other”) are **heuristic and qualitative**, derived from behavioral probes and human‑judged examples; they are vulnerable to **confounding factors** such as task‑specific biases, dataset artifacts, and architecture‑specific inductive biases.[4](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v1)[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

---



- Computing **K‑FAC per MLP weight matrix** over a full dataset requires:  
  - one **forward‑backward pass per example** (or per batch) to accumulate activation–gradient covariances,  
  - and **eigendecompositions** of large covariance matrices per layer.  
  This is already **GPU‑intensive even for small‑to‑medium LMs** and scales poorly with model size and dataset size.[5](https://news.ycombinator.com/item?id=45845835)[2](https://arxiv.org/html/2510.24256v1)[4](https://news.ycombinator.com/item?id=45845800)
- For **larger Transformers or SLMs with many MLP blocks**, the method quickly becomes **infeasible without substantial GPU memory/compute** unless one uses approximations (e.g., block‑diagonal K‑FAC, low‑rank approximations, or subsampling the dataset), which themselves introduce **threats to validity** (e.g., misranking curvature directions or missing subtle memorization modes).[5](https://news.ycombinator.com/item?id=45845835)[2](https://arxiv.org/html/2510.24256v1)[4](https://news.ycombinator.com/item?id=45845800)
- The paper notes that **sweeping over which layers to edit** relies on having memorization labels (or at least a labeled subset) to evaluate edit effectiveness; this multiplies compute cost and limits applicability to settings where such labels are cheap to obtain, contradicting the goal of fully unsupervised, scalable memorization removal.[2](https://arxiv.org/html/2510.24256v1)[4](https://news.ycombinator.com/item?id=45845800)

---



- The **“full‑rank edit”** using K‑FAC editing preserves expressivity better than SVD‑based pruning in the reported experiments, but this may not hold for very small SLMs where low‑rank representations are already compressed and deleting low‑curvature directions can disproportionately harm generalization.[4](https://news.ycombinator.com/item?id=45845800)[2](https://arxiv.org/html/2510.24256v1)
- Because the method is **heavily tuned to the specific architecture and dataset** used in the paper, your SLM‑focused adaptation may face **external‑validity issues**: different tokenizers, vocabularies, training data, or optimization histories can alter the curvature spectrum and thus either weaken mitigation or distort the “reasoning vs. memorization” interpretation.[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2510.24256v1)[4](https://news.ycombinator.com/item?id=45845800)

---



&nbsp;