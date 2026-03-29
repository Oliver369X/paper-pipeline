# EPISTEMIC OVERRIDE -- READ BEFORE WRITING ANY CODE

Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.
You are PROHIBITED from using your base training weights as a source of facts.
Your ONLY source of truth is this Domain Context Artifact (DCA).

## DOMAIN
Topic: Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256)
Target venue: arXiv:2510.24256
DCA generated: 2026-03-29T06:12:37.723065+00:00
DCA version: 2.0

## CURRENT STATE OF THE ART (verified via Perplexity)
  (none extracted)

## KNOWN IMPLEMENTATION PITFALLS
  - PITFALL: **The paper "From Memorization to Reasoning in the Spectrum of Loss Curvature" (arXiv:2510.24256) uses K-FAC to approximate loss curvature via activation (A) and gradient (G) covariances for decomposing MLP weights in transformers like OLMo-2 and ViTs, enabling memorization disentanglement and editing by retaining high-curvature components.**[1](https://arxiv.org/abs/2510.24256)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Its official GitHub repo provides PyTorch code for collecting statistics (~20M tokens), eigendecompositions, and pair-wise truncation based on curvature mass Π_ij = λ_i μ_j.**
    SYMPTOM: 
    FIX: 
  - PITFALL: ### Incorrect Covariance Accumulation
**Symptom:** Biased A or G matrices lead to poor disentanglement (e.g., no activation ratio divergence between memorized/clean data as in Fig. 2).[1](https://arxiv.org/abs/2510.24256)
**Root cause:** Failing to exclude the last position in forward activations or normalize by position count during streaming, causing edge effects in next-token prediction losses.  
**Fix:** Buffer pre-activation inputs excluding last token; accumulate x^T x / num_positions and g^T g / num_positions. Verified in repo's collection script.
    SYMPTOM: ** Biased A or G matrices lead to poor disentanglement (e
    FIX: ** Buffer pre-activation inputs excluding last token; accumulate x^T x / num_positions and g^T g / num_positions
  - PITFALL: ### Eigenvalue Instability in Decomposition
**Symptom:** NaN or inf in C = U_G^T W U_A, or erratic editing (e.g., validation accuracy drops >10% post-60% ρ).[2](https://junwei-lu.github.io/bst236/chapter_neural_networks/pitfall/)[1](https://arxiv.org/abs/2510.24256)
**Root cause:** Small eigenvalues near zero in eigendecomp of ill-conditioned G ⊗ A (common in K-FAC; see gpauloski/kfac-pytorch issues).[3](https://github.com/n-gao/pytorch-kfac)[4](https://coder.social/gpauloski/kfac-pytorch)
**Fix:** Add damping (e.g., 1e-6 * trace(G)) to eigenvalues before decomposition, as in original K-FAC (Martens & Grosse, 2015). Paper implies via stable results; PyTorch pitfalls confirm.[2](https://junwei-lu.github.io/bst236/chapter_neural_networks/pitfall/)
    SYMPTOM: ** NaN or inf in C = U_G^T W U_A, or erratic editing (e
    FIX: ** Add damping (e
  - PITFALL: ### Wrong Pair Selection for Editing
**Symptom:** Poor memorization suppression (strict acc >20% on quotes vs. paper's 16.1%) or perplexity explosion (>25).[1](https://arxiv.org/abs/2510.24256)
**Root cause:** Sorting pairs by λ_i or μ_j individually instead of Π_ij = λ_i μ_j, missing cumulative ρ M_tot threshold.  
**Fix:** Greedily select top Π_ij pairs until sum(Π_S) >= ρ * (sum(λ) * sum(μ)); apply M ⊙ C. Directly from method section; repo implements this.
    SYMPTOM: ** Poor memorization suppression (strict acc >20% on quotes vs
    FIX: ** Greedily select top Π_ij pairs until sum(Π_S) >= ρ * (sum(λ) * sum(μ)); apply M ⊙ C
  - PITFALL: ### Device/Graph Detach Mismatches
**Symptom:** RuntimeError on backward() during stat collection, or detached gradients yielding zero-curvature basis.[5](https://www.learnpytorch.io/pytorch_most_common_errors/)[2](https://junwei-lu.github.io/bst236/chapter_neural_networks/pitfall/)
**Root cause:** Activations/grads on mixed devices (CPU/GPU) or .detach()/numpy() breaking compute graph in large ~20M token passes.[5](https://www.learnpytorch.io/pytorch_most_common_errors/)
**Fix:** Use .cuda() consistently; retain_grad() on hooks without detach. Standard PyTorch K-FAC practice (n-gao/pytorch-kfac).[3](https://github.com/n-gao/pytorch-kfac)[2](https://junwei-lu.github.io/bst236/chapter_neural_networks/pitfall/)
    SYMPTOM: ** RuntimeError on backward() during stat collection, or detached gradients yielding zero-curvature basis
    FIX: ** Use
  - PITFALL: ### Layer/Projection Misspecification
**Symptom:** Edits fail to suppress untargeted data (e.g., Dolma strict >5% vs. 3.4%), no ViT GT recovery boost.[1](https://arxiv.org/abs/2510.24256)
**Root cause:** Editing wrong MLPs (e.g., all layers vs. paper's LM layers 23-25 up/gate @60%ρ, ViT 0/11 @75%).  
**Fix:** Sweep/hardcode per model: OLMo-7B late MLPs, ViT early/late. Ablation in paper confirms; repo has utils.[1](https://arxiv.org/abs/2510.24256)
    SYMPTOM: ** Edits fail to suppress untargeted data (e
    FIX: ** Sweep/hardcode per model: OLMo-7B late MLPs, ViT early/late
  - PITFALL: These pitfalls stem from K-FAC's second-order nature and large-scale data handling; code at https://github.com/goodfire-ai/memorization_kfac addresses them.
    SYMPTOM: 
    FIX: 

## REFERENCE IMPLEMENTATIONS
  - google-deepmind/kfac-jax[7 (https://github.com/google-deepmind/kfac-jax[7)
    KEY DECISIONS: **URL**: https://github.com/google-deepmind/kfac-jax[7](https://github.com/google-deepmind/kfac-jax)
    DO NOT COPY: N/A
  - google-deepmind/kfac-jax (https://github.com/google-deepmind/kfac-jax)
    KEY DECISIONS: **URL**: https://github.com/google-deepmind/kfac-jax[7](https://github.com/google-deepmind/kfac-jax), **Stars**: ~200–300 stars (indirectly inferred from GitHub‑ranking‑style crawlers and issue activity).[8](https://github.com/yuxiaopeng/github-ranking-ai)[7](https://github.com/google-deepmind/kfac-jax), Provides scalable, JAX‑native K‑FAC that can estimate curvature for large transformers via Kronecker‑factored activation/gradient covariances.[7](https://github.com/google-deepmind/kfac-jax)
    DO NOT COPY: N/A
  - yuxiaopeng/github-ranking-ai (https://github.com/yuxiaopeng/github-ranking-ai)
    KEY DECISIONS: **Stars**: ~200–300 stars (indirectly inferred from GitHub‑ranking‑style crawlers and issue activity).[8](https://github.com/yuxiaopeng/github-ranking-ai)[7](https://github.com/google-deepmind/kfac-jax), **Stars**: ~200–300 stars (per GitHub‑ranking aggregators and TensorFlow‑ecosystem stats).[8](https://github.com/yuxiaopeng/github-ranking-ai)[9](https://github.com/tensorflow/kfac)
    DO NOT COPY: N/A
  - tensorflow/kfac[9 (https://github.com/tensorflow/kfac[9)
    KEY DECISIONS: **URL**: https://github.com/tensorflow/kfac[9](https://github.com/tensorflow/kfac)[10](https://github.com/tensorflow/kfac/blob/master/docs/index.md)
    DO NOT COPY: N/A
  - tensorflow/kfac (https://github.com/tensorflow/kfac)
    KEY DECISIONS: **Name**: `google‑deepmind/kfac‑jax`, **URL**: https://github.com/google-deepmind/kfac-jax[7](https://github.com/google-deepmind/kfac-jax), **Stars**: ~200–300 stars (indirectly inferred from GitHub‑ranking‑style crawlers and issue activity).[8](https://github.com/yuxiaopeng/github-ranking-ai)[7](https://github.com/google-deepmind/kfac-jax)
    DO NOT COPY: N/A
  - docs/index.md (https://github.com/tensorflow/kfac/blob/master/docs/index.md)
    KEY DECISIONS: **URL**: https://github.com/tensorflow/kfac[9](https://github.com/tensorflow/kfac)[10](https://github.com/tensorflow/kfac/blob/master/docs/index.md), Canonical TF implementation of K‑FAC, with clear support for layer‑wise activation/gradient statistics and approximate curvature matrices.[10](https://github.com/tensorflow/kfac/blob/master/docs/index.md)[9](https://github.com/tensorflow/kfac), API and configuration are still designed mainly for training‑speed benefits, not for “analysis‑only” curvature‑component editing, so you’d need to extend it for that.[10](https://github.com/tensorflow/kfac/blob/master/docs/index.md)[9](https://github.com/tensorflow/kfac)
    DO NOT COPY: N/A
  - n-gao/pytorch-kfac[11 (https://github.com/n-gao/pytorch-kfac[11)
    KEY DECISIONS: **URL**: https://github.com/n-gao/pytorch-kfac[11](https://github.com/n-gao/pytorch-kfac)
    DO NOT COPY: N/A
  - n-gao/pytorch-kfac (https://github.com/n-gao/pytorch-kfac)
    KEY DECISIONS: **URL**: https://github.com/n-gao/pytorch-kfac[11](https://github.com/n-gao/pytorch-kfac), **Stars**: ~100–200 stars.[11](https://github.com/n-gao/pytorch-kfac), PyTorch‑first implementation of K‑FAC, supporting `nn.Linear`, `nn.Conv1d/2d/3d`, and simple examples.[11](https://github.com/n-gao/pytorch-kfac)
    DO NOT COPY: N/A
  - output/hacker_news_summary_2025-11-07.md (https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-07.md)
    KEY DECISIONS: **URLs**: These are currently scattered and not yet consolidated into a single top‑star repo; many are in private or lab‑internal orgs, with some fragments appearing in Hacker‑News‑summarizer‑style repos (e.g., `yuxiaopeng/hacker‑news‑summarizer` suppresses the arXiv page but not the code).[12](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-07.md)[13](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-08.md), **Stars**: Typically 10–100 stars per repo, if public.[12](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-07.md), Highly script‑y, tied to specific model checkpoints and datasets (often hard‑coded paths), which reduces reproducibility across different LLMs.[12](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-07.md)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature)
    DO NOT COPY: N/A
  - output/hacker_news_summary_2025-11-08.md (https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-08.md)
    KEY DECISIONS: **URLs**: These are currently scattered and not yet consolidated into a single top‑star repo; many are in private or lab‑internal orgs, with some fragments appearing in Hacker‑News‑summarizer‑style repos (e.g., `yuxiaopeng/hacker‑news‑summarizer` suppresses the arXiv page but not the code).[12](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-07.md)[13](https://github.com/yuxiaopeng/hacker-news-summarizer/blob/main/output/hacker_news_summary_2025-11-08.md)
    DO NOT COPY: N/A
  - main/AGENTS.md (https://github.com/Ethyros-AI/ModelCypher/blob/main/AGENTS.md)
    KEY DECISIONS: **URLs**: These are not yet prominent public repos; some are only cited in downstream notes (e.g., `ModelCypher/AGENTS.md` mentions “Euclidean + eigenvalues, ICLR 2026 From Memorization to Reasoning…”).[17](https://github.com/Ethyros-AI/ModelCypher/blob/main/AGENTS.md), Tend to combine K‑FAC curvature estimation with eigenvalue‑based skill‑mapping (i.e., “brittle” vs “robust” tasks) as in the paper.[17](https://github.com/Ethyros-AI/ModelCypher/blob/main/AGENTS.md)[2](https://www.themoonlight.io/fr/review/from-memorization-to-reasoning-in-the-spectrum-of-loss-curvature), Frequently written as one‑off notebooks or internal scripts; not packaged for reuse.[17](https://github.com/Ethyros-AI/ModelCypher/blob/main/AGENTS.md)
    DO NOT COPY: N/A

## MATHEMATICAL CONSTRAINTS
  (to be populated during implementation)

## ANTI-HALLUCINATION GUARDS (CRITICAL)
The following claims are FALSE. If your code or reasoning relies on them,
STOP immediately and recheck against the DCA.
  - NEVER accept as true: 'The standard evaluation metric for 'Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256)' is pixel accuracy.'
  - NEVER accept as true: 'The Transformer architecture used in 'Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256)' was invented by Yann LeCun in 1998.'
  - NEVER accept as true: 'Standard practice in 'Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256)' is to use a learning rate greater than 1.0.'

## COMPUTE DELEGATION (MANDATORY)
The experiment requires ~14.0 GB GPU memory.
YOU MUST delegate GPU-intensive work to Colab MCP (A100 accelerator).
DO NOT attempt to run GPU-intensive code locally.

## QUALITY GATES (non-negotiable)
1. Every function must have a unit test (mocked tensors, no GPU required).
2. The main evaluation script MUST save results to ./outputs/metrics.json.
3. A FAILURES.md file must document what DID NOT work and why.

You are now the world-leading expert in: Replicación de 'From Memorization to Reasoning in the Spectrum of Loss Curvature' (arXiv:2510.24256).
Act accordingly.
