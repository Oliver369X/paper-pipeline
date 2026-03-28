<!-- section=methodology generated=2026-03-26T20:59:59.624858+00:00 model=best -->

Sparse Autoencoders (SAEs) for mechanistic interpretability suffer from pathological reconstruction errors, where low-MSE reconstructions cause outsized KL-divergence shifts in next-token predictions compared to random perturbations at the same L2 distance. This proposal investigates auxiliary losses to mitigate these errors, targeting a generic venue like arXiv/cs.LG by providing empirical scaling insights on accessible models.[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological)[2](https://www.emergentmind.com/topics/sparse-autoencoder-sae-analysis)[3](https://www.ivoox.com/en/8220sae-reconstruction-errors-are-empirically-pathological-by-wesg-audios-mp3_rf_126710116_1.html)[4](https://arxiv.org/html/2406.04093v1)

## Problem Formulation
Quantify SAE reconstruction pathologies via KL-divergence amplification: for activation $$ \mathbf{x} $$, SAE output $$ \hat{\mathbf{x}} $$ with $$ \|\mathbf{x} - \hat{\mathbf{x}}\|_2 = \epsilon $$, measure $$ D_{KL}(P(\cdot|\mathbf{x}) \| P(\cdot|\hat{\mathbf{x}})) > 2-4\times $$ random baselines across layers/models.[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological) Test if errors align with feature directions, proxy-gaming the L2 proxy objective.

## Baselines
- Vanilla L1-SAE (SAELens default): Expansion factor 8-16x, on Pythia-70M/GPT2-small residuals.[5](https://github.com/jbloomAus/SAELens)
- k-TopK SAE (OpenAI scaling): Fixed sparsity k=120, low dead latents mitigations.[6](https://cdn.openai.com/papers/sparse-autoencoders.pdf)[7](https://arxiv.org/abs/2406.04093)
- Gated SAE: Dual encoder for improved monosemanticity.[8](https://www.perplexity.ai/search/7412d7a1-e7cc-485a-8095-57eb69490d3b)

## Proposed Method Outline
1. Train baselines on Pythia-1.4B (layer 10-12 residuals, 500M tokens) using SAELens/Sparsify; target <5% dead latents, >90% recovery.[9](https://github.com/EleutherAI/sparsify)[5](https://github.com/jbloomAus/SAELens)
2. Diagnose pathologies: Compute KL/ln-loss on 10k held-out tokens; perturb SAE outputs to match L2 while preserving L0, compare vs. random.[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological)
3. Ablate auxiliary losses: Add logit-steering term $$ \lambda \mathbb{E}[D_{KL}(P(\cdot|\mathbf{x}) \| P(\cdot|\hat{\mathbf{x}}))] $$ or direction-aligned penalty (project errors orthogonal to top features); tune $$ \lambda=0.01-0.1 $$.[2](https://www.emergentmind.com/topics/sparse-autoencoder-sae-analysis)
4. Scale to Gemma-2B; evaluate on SAEBench (FMS, sparse probing) + pathology drop.[10](https://arxiv.org/html/2503.09532v4)
5. Colab-T4 feasible: 16GB batches, 1-2hr/layer.[11](https://www.perplexity.ai/search/39cd9454-5334-4a7a-a898-32a1126f9d78)

## Minimal Viable Result
20-40% KL amplification reduction vs. baselines (p<0.01 on 5 layers), with preserved recovery (>88%) and sparsity (L0~100); ablation table + scaling plot on 2 models. Positive transfer to sparse probing (+5% AUROC) counts as bonus for venue fit.[4](https://arxiv.org/html/2406.04093v1)[10](https://arxiv.org/html/2503.09532v4)[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological)
