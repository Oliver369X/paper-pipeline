<!-- section=experiments generated=2026-03-27T20:38:03.035903+00:00 model=best -->

This experiment analyzes loss curvature changes during the memorization-to-reasoning transition in language models, building on K-FAC approximations of the Hessian to identify sharp (memorization) vs. flat (reasoning) directions. It uses scalable edits to probe phase shifts, suitable for accessible models like OLMo-2 7B.[1](https://arxiv.org/html/2510.24256v1)[2](https://arxiv.org/abs/2510.24256)

## Objectives
Quantify how loss curvature evolves from high (sharp basins for memorized data) to low/moderate (flatter for reasoning). Identify transition thresholds via double descent-like curves and activation patterns. Test interventions to suppress memorization while preserving reasoning.[3](https://arxiv.org/html/2510.24256v2)[4](https://deep-learning-mit.github.io/staging/blog/2023/double_descent/)[1](https://arxiv.org/html/2510.24256v1)

## Baselines
- Unedited baseline model (full weights).
- SVD truncation (prune low singular values, data-free).[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)
- BalancedSubnet (BSN): Supervised unlearning with forget/retain sets.[1](https://arxiv.org/html/2510.24256v1)
- SAM (Sharpness-Aware Minimization): Train with curvature regularization.[1](https://arxiv.org/html/2510.24256v1)

## Setup
Train/fine-tune small-to-medium LMs (e.g., OLMo-1B/7B) on mixtures: 70% clean Dolma/Pile (generalization), 30% duplicates/noised labels (induce memorization). Vary interpolation regime by scaling data repeats (1x to 100x) or model size (100M-7B params). Compute K-FAC covariances (A=activation, G=gradient) on 20M tokens per checkpoint. Edit MLPs in late layers (23-25) at 60% curvature mass retention (ρ=0.6).[3](https://arxiv.org/html/2510.24256v2)[1](https://arxiv.org/html/2510.24256v1)

## Metrics
- Memorization: Strict/loose accuracy (exact/75% match on heldout prefixes), Levenshtein distance.[1](https://arxiv.org/html/2510.24256v1)
- Reasoning: Accuracy on GSM8K (math), TriviaQA (closed-book facts), Boar Etruscan (logic); perplexity on Pile10k.
- Curvature: Trace/top eigenvalue of K-FAC FIM (G⊗A); activation ratios (mem/clean on low vs. high eigendirections).[3](https://arxiv.org/html/2510.24256v2)
- Generalization: MMLU-Pro, validation PPL drop post-edit.

## Ablations
- Curvature threshold: Vary ρ (40-80%) to map transition sharpness.
- Data regime: Clean vs. duplicate-heavy mixtures; noised labels (10-50%).
- Edit scope: All MLPs vs. early/late layers; up/gate/down proj only.
- Model scale: 1B vs. 7B to check double descent.[6](https://chrisliu298.ai/neurips2023_opt_poster.pdf)

## Budget
Target 100 GPU-hours (A100s): K-FAC on 20M tokens (~2h/model), 10 runs/ablation (fine-tune 1-2 epochs each), edits/evals (~1h). Use Colab/Prodigy for student access; batch parallelize covariance collection. Scale down to 1B model if needed.[3](https://arxiv.org/html/2510.24256v2)

## Results Table Outline

| Configuration | Memorization Strict Acc ↓ (%) | Reasoning Acc (GSM8K) ↓ (%) | PPL ↑ | Max Curvature (Trace) ↓ | Activation Ratio (Low Eigens) ↑ |
|---------------|------------------------------|-----------------------------|-------|-------------------------|---------------------------------|
| Baseline     | 99.9                | 100 (baseline)     | 19.04 | 1.0 (norm)[3](https://arxiv.org/html/2510.24256v2)     | 1.0[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)                     |
| K-FAC ρ=0.6  | 3.4                 | 66-74              | 22.84 | 0.6                    | 1.6x (mem/clean)       |
| BSN          | 6.0                 | ~80                | 23.59 | N/A                    | N/A                            |
| SVD          | 3.0                 | ~85                        | 22.49 | N/A                    | 1.2x[5](https://www.semanticscholar.org/paper/From-Memorization-to-Reasoning-in-the-Spectrum-of-Merullo-Vatsavaya/6d1a57fc3fa4487d17a56c5b178a99bd25265057)                    |
| High Dups    | 95                          | 50                         | 25    | 1.5                    | 2.0x                           |
