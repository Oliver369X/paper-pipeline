<!-- section=experiments generated=2026-03-27T18:07:32.581501+00:00 model=best -->

This experiment plan uses K-FAC (Kronecker-Factored Approximate Curvature) to approximate loss landscape curvature in SLMs, targeting low-curvature directions linked to memorization for weight editing or regularization, as low-curvature components correlate with rote memorization while high-curvature ones support generalization.[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://www.youtube.com/watch?v=5kWG5Hpi-Uo)[3](https://www.linkedin.com/posts/charlesmartin14_%F0%9D%97%99%F0%9D%97%BF%F0%9D%97%BC%F0%9D%97%BA-%F0%9D%97%A0%F0%9D%97%B2%F0%9D%97%BA%F0%9D%97%BC%F0%9D%97%BF%F0%9D%97%B6%F0%9D%98%87%F0%9D%97%AE%F0%9D%98%81%F0%9D%97%B6%F0%9D%97%BC%F0%9D%97%BB-%F0%9D%98%81%F0%9D%97%BC-activity-7392365987003744256-LuAU)

## Experiment Setup
Train or fine-tune SLMs like SmolLM2-1.7B or Phi-3.5-Mini-3.8B on a memorization-prone dataset (e.g., subset of Dolma or Pile with duplicates) to induce overfitting. Collect K-FAC statistics (activation/gradient covariances A and G) on ~20M tokens from training data via forward/backward passes on target MLP layers (e.g., final 2-3 layers' gate/up projections). Edit weights by eigendecomposing to curvature basis, truncating low-curvature components (e.g., retain top 60% energy), then reconstruct.[4](https://arxiv.org/html/2510.24256v2)[5](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)[6](https://news.ycombinator.com/item?id=45845835)[7](https://huggingface.co/blog/jjokah/small-language-model)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

## Suggested Baselines
- **No intervention**: Untuned SLM as baseline for memorization levels.[4](https://arxiv.org/html/2510.24256v2)
- **SVD pruning**: Singular value decomposition on weights, retaining top components by magnitude.[4](https://arxiv.org/html/2510.24256v2)
- **Balanced Subnet (BSN)**: Supervised unlearning baseline that balances forget/retain sets.[4](https://arxiv.org/html/2510.24256v2)
- **Standard regularization**: Weight decay or dropout during fine-tuning.[8](https://arxiv.org/abs/1602.01407)

## Key Metrics
Primary: Memorization suppression via strict/loose extractability (% verbatim recitation on held-out memorized sequences, e.g., Dolma validation or custom duplicates) and nDCG@10 for ranked retrieval. Secondary: Perplexity on retain set (Pile-10k subset), downstream tasks (e.g., fact retrieval, arithmetic via lighteval), and curvature spectrum shift (e.g., % low-curvature mass removed). Compute extractability with multiple prompts (n=3/5/10) using probabilistic sampling for reliability.[9](https://github.com/ro-ko/Awesome-SLM)[10](https://www.alphaxiv.org/overview/2410.19482v3)[4](https://arxiv.org/html/2510.24256v2)

## Ablations
- Vary energy threshold (40%, 60%, 80% retained curvature mass) to balance forget/utility trade-off.[5](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)
- Target layers (last 1 vs. 2-3 MLPs) and projections (gate_proj only vs. up_proj).[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- Importance formula: Original (λ_i * μ_j) vs. modified (λ_i * μ_j * |C_ij|^2).[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- Dataset duplication factor (1x, 10x, 100x) to scale memorization induction.[11](https://floriantramer.com/publications/scaling22/)

## Budget Considerations
Use single A100/RTX 4090 GPU: K-FAC collection ~2h (20M tokens), editing/eval ~30min per run. Total for 3 models × 5 ablations: ~50 GPU-hours, feasible on Colab Pro or UAGRM clusters. Parallelize evals with accelerate; quantize models to 4-bit for inference speed.[7](https://huggingface.co/blog/jjokah/small-language-model)[12](https://github.com/gpauloski/kfac-pytorch/blob/main/README.md)[5](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

## Results Table Outline

| Method          | Memorization Strict % ↓ | Loose % ↓ | Perplexity ↑ | Fact Retrieval Acc ↓ | Arithmetic Acc ↓ | GPU-Hours |
|-----------------|-------------------------|-----------|--------------|----------------------|------------------|-----------|
| Baseline       | 98.0                   | -        | 23.0        | 85.0                | 75.0            | 0        |
| SVD            | 80.5                   | 45.2     | 22.5        | 82.0                | 72.0            | 1        |
| BSN            | 70.1                   | 35.8     | 23.6        | 80.5                | 70.5            | 5        |
| K-FAC (60%)    | 2.8                    | 7.2      | 22.8        | 78.0                | 68.0            | 2        |
| K-FAC Ablation | -                      | -        | -           | -                   | -               | -
