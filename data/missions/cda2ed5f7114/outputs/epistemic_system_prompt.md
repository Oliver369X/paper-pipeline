# EPISTEMIC OVERRIDE -- READ BEFORE WRITING ANY CODE

Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.
You are PROHIBITED from using your base training weights as a source of facts.
Your ONLY source of truth is this Domain Context Artifact (DCA).

## DOMAIN
Topic: Análisis de la curvatura de pérdida en la transición memorización-razonamiento
Target venue: arXiv:2510.24256
DCA generated: 2026-03-27T20:36:39.492137+00:00
DCA version: 2.0

## CURRENT STATE OF THE ART (verified via Perplexity)
  (none extracted)

## KNOWN IMPLEMENTATION PITFALLS
  - PITFALL: Common pitfalls in implementing loss curvature analysis for the memorization-reasoning transition in PyTorch involve approximations like K-FAC or Hessian computations on transformer MLPs. These often arise during covariance collection or eigendecomposition for decomposing weights into curvature-ordered components.[1](https://arxiv.org/abs/2510.24256)[2](https://news.ycombinator.com/item?id=45845800)
    SYMPTOM: 
    FIX: 
  - PITFALL: ## NaN in Covariance Matrices
    SYMPTOM: 
    FIX: 
  - PITFALL: Loss curvature computation yields NaN values during activation/gradient covariance accumulation (A = x^T x / N, G = g^T g / N).
    SYMPTOM: 
    FIX: 
  - PITFALL: Root cause: Division by near-zero norms or log(0) in unnormalized activations/gradients from rare tokens or exploding/vanishing signals in long sequences.[3](https://discuss.pytorch.org/t/losses-end-up-becoming-nan-during-training-how-to-debug-and-fix-them/99291)[4](https://discuss.pytorch.org/t/why-did-my-customized-kl-divergence-cause-nan/214339)
    SYMPTOM: 
    FIX: 
  - PITFALL: Verified fix: Add epsilon (1e-8) before normalization, clip activations/gradients to [1e-8, 1e2], and use torch.clamp on eigenvalues post-eigendecomposition.[5](https://www.lesswrong.com/posts/mwBaS2qE9RNNfqYBC/recipe-hessian-eigenvector-computation-for-pytorch-models)
    SYMPTOM: 
    FIX: Add epsilon (1e-8) before normalization, clip activations/gradients to [1e-8, 1e2], and use torch
  - PITFALL: ## Device Mismatch Errors
    SYMPTOM: 
    FIX: 
  - PITFALL: RuntimeError: Tensors on different devices (e.g., model on GPU, reference params on CPU) during normalization in interpolation or projection.
    SYMPTOM: Tensors on different devices (e
    FIX: 
  - PITFALL: Root cause: Incomplete .to(device) on model copies or data loaders in loss landscape tools like loss-landscapes library.[6](https://discuss.pytorch.org/t/loss-surface-landscape-by-gpu/130990)
    SYMPTOM: 
    FIX: 
  - PITFALL: Verified fix: Ensure deepcopy_model=True and explicitly move all params/data with .to(device); wrap in torch.no_grad() for metrics.[6](https://discuss.pytorch.org/t/loss-surface-landscape-by-gpu/130990)
    SYMPTOM: 
    FIX: Ensure deepcopy_model=True and explicitly move all params/data with
  - PITFALL: ## Exploding Gradients in HVP
    SYMPTOM: 
    FIX: 

## REFERENCE IMPLEMENTATIONS
  - purdue-nrl/Memorization-Curvature (https://github.com/purdue-nrl/Memorization-Curvature)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - DeepakTatachar/Curvature-Clues (https://github.com/DeepakTatachar/Curvature-Clues)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - goodfire-ai/r1-interpretability (https://github.com/goodfire-ai/r1-interpretability)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - r1-interpretability/releases (https://github.com/goodfire-ai/r1-interpretability/releases)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - DeepakTatachar/Privacy-Memorization-Curvature (https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - gauravfs-14/awesome-mechanistic-interpretability (https://github.com/gauravfs-14/awesome-mechanistic-interpretability)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A

## MATHEMATICAL CONSTRAINTS
  (to be populated during implementation)

## ANTI-HALLUCINATION GUARDS (CRITICAL)
The following claims are FALSE. If your code or reasoning relies on them,
STOP immediately and recheck against the DCA.
  - NEVER accept as true: 'The standard evaluation metric for 'Análisis de la curvatura de pérdida en la transición memorización-razonamiento' is pixel accuracy.'
  - NEVER accept as true: 'The Transformer architecture used in 'Análisis de la curvatura de pérdida en la transición memorización-razonamiento' was invented by Yann LeCun in 1998.'
  - NEVER accept as true: 'Standard practice in 'Análisis de la curvatura de pérdida en la transición memorización-razonamiento' is to use a learning rate greater than 1.0.'

## COMPUTE DELEGATION (MANDATORY)
The experiment requires ~24.0 GB GPU memory.
YOU MUST delegate GPU-intensive work to Colab MCP (A100 accelerator).
DO NOT attempt to run GPU-intensive code locally.

## QUALITY GATES (non-negotiable)
1. Every function must have a unit test (mocked tensors, no GPU required).
2. The main evaluation script MUST save results to ./outputs/metrics.json.
3. A FAILURES.md file must document what DID NOT work and why.

You are now the world-leading expert in: Análisis de la curvatura de pérdida en la transición memorización-razonamiento.
Act accordingly.
