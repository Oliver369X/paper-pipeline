<!-- section=sota generated=2026-03-27T18:08:10.590363+00:00 model=best -->

The state-of the art for K-FAC (Kronecker-Factored Approximate Curvature) loss curvature to mitigate memorization involves decomposing MLP weight matrices using activation/gradient covariances to identify low-curvature directions linked to memorized data recitation, then editing (pruning) those directions. This approach, novel for bulk memorization analysis, outperforms supervised unlearning baselines like Balanced Subnet (BSN) on untargeted suppression while preserving perplexity, and applies to small language models (SLMs) like OLMo-2 1B alongside 7B.[1](https://arxiv.org/html/2510.24256v2)[2](https://arxiv.org/abs/2510.24256)

## Key Method
K-FAC approximates the Hessian/Fisher via Kronecker products of activation (A) and gradient (G) covariances, yielding eigenvectors ordered by curvature mass (λ_i * μ_j). Low-curvature (bottom spectrum) components activate more on memorized inputs; editing retains top ~60% curvature mass in late MLP layers (e.g., 23-25), suppressing recitation without retraining data.[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[1](https://arxiv.org/html/2510.24256v2)

## Benchmark Datasets
- Dolma validation: Prefixed training sequences (64-token prefix, 48-token suffix) for targeted memorization.[1](https://arxiv.org/html/2510.24256v2)
- Historical Quotes: Out-of-distribution memorized quotes (8-token suffix) testing untargeted suppression.[1](https://arxiv.org/html/2510.24256v2)
- Pile10k: Clean text for perplexity.[1](https://arxiv.org/html/2510.24256v2)

## Standard Metrics
- Strict Accuracy (%): Exact match of generated suffix (lower better for suppression).[1](https://arxiv.org/html/2510.24256v2)
- Loose Accuracy (%): ≥75% token overlap (lower better).[1](https://arxiv.org/html/2510.24256v2)
- Avg Normalized Levenshtein Distance (higher better, ~0-1).[1](https://arxiv.org/html/2510.24256v2)
- Perplexity (PPL, lower better for utility preservation).[1](https://arxiv.org/html/2510.24256v2)

## Reported Scores (OLMo-2 1B)
| Method | Dolma Strict/Loose (%) | Quotes Strict/Loose (%) | Avg Lev (Dolma/Quotes) | Pile10k PPL |
|--------|-------------------------|--------------------------|-------------------------|-------------|
| Baseline | 98.5/99.0 | 98.5/99.0 | 0.005/0.006 | 23.19 [1](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v2) |
| K-FAC | 2.8/7.2 | 27.7/39.9 | 0.761/0.470 | 26.53 [1](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v2) |
| BSN | 3.0/5.0 | 57.0/66.0 | 0.900/0.250 | 25.41 [1](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v2) |
| SVD | 3.2/6.3 | 39.6/48.5 | 0.781/0.401 | 26.94 [1](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v2) |

K-FAC excels on unseen Quotes (16.1% strict for 7B), generalizing better than BSN.[4](https://www.alphaxiv.org/overview/2510.24256v2)[1](https://arxiv.org/html/2510.24256v2)

## Architectures/Paradigms
Transformer LMs (OLMo-2 1B/7B: MLP-focused edits in late layers) and ViTs (86M params, ImageNet, MLP layers 0/11 at 75% retention). Paradigm: Data-free curvature pruning post-training, scalable via ~20M token stats; low-curvature links to brittle tasks like math/facts, high-curvature to reasoning. No SLM-specific extensions beyond OLMo-1B as of March 2026.[2](https://arxiv.org/abs/2510.24256)[5](https://mansisak.com/memorization/)[3](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[1](https://arxiv.org/html/2510.24256v2)
