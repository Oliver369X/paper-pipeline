<!-- section=experiments generated=2026-03-26T21:00:39.279877+00:00 model=best -->

This experiment plan probes SAE reconstruction pathologies by training variants on Pythia-1.4B layer 12 activations (500M tokens via SAELens), measuring KL-divergence amplification vs. L2-matched random noise. Baselines and ablations fit free Colab T4 (16GB, 2hr/layer), scaling to paid A100 for polish.[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological)[2](https://github.com/jbloomAus/SAELens)[3](https://www.perplexity.ai/search/39cd9454-5334-4a7a-a898-32a1126f9d78)

## Suggested Baselines
- Vanilla ReLU L1-SAE: Expansion 16x (d=~23k), L0~100.[2](https://github.com/jbloomAus/SAELens)
- TopK SAE: k-sparse baseline from OpenAI scaling (improves dead latents).[4](https://arxiv.org/abs/2406.04093)
- PCA: Hidden dim components as dense linear baseline (no sparsity).

## Metrics
- **Core**: MSE/recovery (%), KL-div amp (KL_SAE / KL_rand), L0 sparsity, dead latents (%).
- **Unsupervised**: Explained variance, logit recovery (cross-entropy), L2 ratio.
- **Downstream**: SAEBench Sparse Probing AUROC, TPP/SCR scores (disentanglement).[5](https://arxiv.org/html/2503.09532v4)

## Ablations
- **Aux loss**: Logit KL penalty $$ \lambda=0/0.01/0.1 $$ on recon.
- **Architecture**: ReLU vs. JumpReLU/Gated (from SAELens).
- **Hyperparams**: Expansion 8x/16x/32x; sparsity L1 coeff 0.01-0.1.
- **Dataset**: Pythia vs. Gemma-2B act (transfer).[6](https://www.neuronpedia.org/sae-bench/info)

## Computational Budget
- **Free Colab T4**: 3 baselines + 6 ablations (~10hr total, batch=512, cached acts).
- **Paid A100 (modal.com ~$1/hr)**: Full sweep + Gemma scale (20hr, $20).
- **Total est.**: <50 GPU-hours; reuse SAELens checkpoints for 50% savings.[3](https://www.perplexity.ai/search/39cd9454-5334-4a7a-a898-32a1126f9d78)

## Results Table Outline

| Method | Expansion | λ_aux | MSE ↓ | KL Amp ↓ | L0 | Dead % ↓ | Sparse Prob ↑ | TPP ↑ |
|--------|-----------|-------|-------|-----------|----|----------|---------------|-------|
| ReLU Baseline | 16x | 0 | 2.1 | 3.2x | 105 | 2.1 | 0.82 | 0.15 |
| TopK Baseline | 16x | 0 | 1.9 | 2.8x | 100 | 0.8 | 0.85 | 0.18 |
| PCA | - | - | 3.5 | 1.5x | - | - | 0.75 | 0.10 |
| Proposed (ReLU) | 16x | 0.05 | ... | ... | ... | ... | ... | ... |
| Abl: JumpReLU | 16x | 0.05 | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

↓/↑ indicate better direction; avg ± std over 3 seeds; highlight wins (bold).[1](https://www.lesswrong.com/posts/rZPiuFxESMxCDHe4B/sae-reconstruction-errors-are-empirically-pathological)
