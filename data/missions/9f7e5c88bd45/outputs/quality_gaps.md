<!-- quality_check: assisted review via same Perplexity stack as sections; not independent empirical validation. See docs/technical/EVALUATION_LAYERS.md -->

The draft outlines a promising extension of K-FAC curvature editing from arXiv:2510.24256 ("From Memorization to Reasoning in the Spectrum of Loss Curvature") to SLMs like Phi-3-mini, but lacks executed experiments and full arXiv formatting.[1](https://arxiv.org/abs/2510.24256)[2](https://arxiv.org/html/2510.24256v2)

## Missing Citations
Draft cites arXiv:2510.24256 extensively but omits key references from the target paper, such as Martens & Grosse (2015) on original K-FAC, Sakarvadia et al. (2025) on BSN baseline (only linked indirectly), and prior curvature-memorization works like Foret et al. (2021), Hochreiter & Schmidhuber (1997), or Keskar et al. (2017).[2](https://arxiv.org/html/2510.24256v2)
- No citations for SLM-specific baselines (e.g., Phi-3 training details from Microsoft, 2024; SmolLM from Hugging Face, 2024).
- Datasets like FineMath, Dolma subsets, or Pile-10k need precise sources (e.g., OLMo mixtures from AllenAI, 2024); tabular datasets mismatch text-focused K-FAC use in target paper.[2](https://arxiv.org/html/2510.24256v2)

## Weak Methodology
K-FAC decomposition correctly mirrors target (project $$C = U_G^\top W U_A$$, mask by $$\Pi_{ij} = \lambda_i \mu_j$$, retain $$\rho=60\%$$), but skips numerical stability fixes like damping or low-rank approx for small SLM covariances (G/A ~3k x 3k for Phi-3), risking instability on limited ~1-5M tokens.[2](https://arxiv.org/html/2510.24256v2)
- Assumes late MLP layers (80% from end) without justifying vs. target sweeps (layers 23-25 in OLMo-7B).
- No handling of post-edit fine-tuning dynamics, noted as needed in target for expressivity.[2](https://arxiv.org/html/2510.24256v2)
- Ignores target insight: low aggregate curvature for memorization (flatter basins across examples), not per-example sharpness.[2](https://arxiv.org/html/2510.24256v2)

## Unclear Experiments
Results table shows placeholder numbers (e.g., K-FAC strict 2.8%) not matching target's OLMo-1B (K-FAC: 2.8/7.2 Dolma, 27.7/39.9 Quotes; PPL 26.53); no reproduction evidence or code links beyond general repos like omrifahn/kfac-memorization-code.[2](https://arxiv.org/html/2510.24256v2)
- Baselines (BSN, SVD) lack hyperparams (target: BSN sparsity 0.0015, LR 0.3; 5 epochs); no stress tests like positional perturbations from Huang et al. (2024).[2](https://arxiv.org/html/2510.24256v2)
- Ablations vague: no exact duplication factors, n= prompts for extractability, or OOMeval suite matching target (MMLU-Pro Math, Boar Etruscan).[2](https://arxiv.org/html/2510.24256v2)
- Budget (~50 GPUh) feasible but unverified; no quantization interaction tests critical for SLMs.[2](https://arxiv.org/html/2510.24256v2)

## Ethical/Safety Issues
Disclaimer notes LLM assistance and unreproducibility, but draft posits YAIS Lab AI safety fit without discussing risks: edited SLMs may degrade reasoning (target: math drops, brittle facts) or resurface memorization post-adaptation.[2](https://arxiv.org/html/2510.24256v2)
- No unlearning privacy analysis (e.g., PII in Dolma/Quotes); overlooks target limitations like synthetic data validity threats.
- Potential dual-use: easy pruning could enable malicious model editing without safeguards.

## Formatting Issues
Lowercase section headers ("methodology", "experiments") violate arXiv LaTeX (use \section{Methodology}); title in Spanish mismatches English target venue cs.CL.[1](https://arxiv.org/abs/2510.24256)
- Inline citations as (url) fail arXiv \cite; use BibTeX.[1](https://arxiv.org/abs/2510.24256)
- Tables inconsistent (e.g., results outline lacks target metrics like nDCG@10); no abstract, intro, related work, or appendices.
- Comments (<!-- -->), disclaimers dominate; remove for submission. Target uses 2-column, full structure (abstract, 10 sections).[2](https://arxiv.org/html/2510.24256v2)
