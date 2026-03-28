<!-- section=methodology generated=2026-03-27T16:29:15.224571+00:00 model=best -->

BalancedSubnet effectively mitigates memorization in language models by pruning weights responsible for regurgitating training data while preserving general performance. This methodology investigates improvements to it, targeting a technical report or ML research venue like arXiv or NeurIPS workshops.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)

## Problem Formulation
Memorization occurs when a language model (LM) encodes training sequences in its weights, enabling verbatim regurgitation upon prompting with prefixes, as defined by (n,k)-memorization where the first k tokens elicit the remaining n-k tokens via greedy decoding.[2](https://mansisak.com/memorization/)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Formally, for an LM $$ M $$ and artifact set $$ s_A $$ (e.g., noised or backdoored sequences from training data $$ D $$), measure % Memorized as $$\frac{\# \text{ elicited artifacts}}{\# \text{ total artifacts}} \times 100$$, where artifacts are perturbations like noise ($$ s_n $$ with ±1 shifts) or backdoors (triggered sequences).[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)
The goal is to edit $$ M $$ post-training to minimize % Memorized on $$ s_A $$ (target: -100% change) while keeping test accuracy/perplexity near baseline (0% change).[2](https://mansisak.com/memorization/)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Baselines
Compare against three classes from prior work:[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)
- **Regularizers** (train-time): Spectral norm, loss truncation, example-tied dropout—slow, often fail to curb memorization without hurting convergence.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
- **Fine-tuning** (post-training): On clean data, extra data, or both—effective but computationally expensive (e.g., 3600s vs. unlearning's <100s).[2](https://mansisak.com/memorization/)
- **Unlearning** (post-training, weight/neuron-based): Greedy, Durable, Subnet, neuron methods (e.g., Hard Concrete, Integrated Gradients)—BalancedSubnet outperforms by balancing memorization removal and performance preservation across model sizes/data types.[2](https://mansisak.com/memorization/)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

| Method Class | Memorization Reduction | Performance Preservation | Speed |
|--------------|-------------------------|---------------------------|-------|
| Regularizers | Poor | Variable | Slow [1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf) |
| Fine-tuning | Good | Good | Slow [2](https://mansisak.com/memorization/) |
| Unlearning (e.g., Subnet) | Good | Moderate | Fast [1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf) |

## Proposed Method Outline
**Core: Implement/Extend BalancedSubnet.** Start with the official GitHub code for TinyMem/Pythia models.[3](https://github.com/msakarvadia/memorization)[2](https://mansisak.com/memorization/)
1. Train baseline TinyMem LMs (2-16 layers, math/language tasks) with artifacts (5-10% noise/backdoors) until memorization emerges (~epochs 50-3500).[2](https://mansisak.com/memorization/)
2. Apply BalancedSubnet: Initialize per-parameter scores (Kaiming uniform), optimize binary mask via straight-through estimator on shuffled memorized + random sequences; loss = LM loss × batch_mask where mask penalizes memorized (-(1-weight)) vs. random (+weight) sequences; drop top-K weights per layer.[2](https://mansisak.com/memorization/)
3. **Novel Extension (for investigation):** Add interpretability—use activation gradients or SAEs to validate pruned subnetworks target memorization circuits; test adaptive K via loss curvature; scale to Gemma-2B with Bolivia-specific data (e.g., local texts) for regional relevance.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Run over 3 seeds, HP tune (K=0.1-1%, epochs=10-100, loss_weight=0.5-0.9).[2](https://mansisak.com/memorization/)

## Minimal Viable Result
On 4-layer TinyMem (math+noise/backdoor), achieve ≥90% memorization reduction (% diff ≤-90) with ≤5% accuracy drop, faster than fine-tuning (<10s avg.); replicate on Pythia-2.8B with ≥50% reduction and <5% perplexity increase.[4](https://arxiv.org/abs/2410.02159v2)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)
Success table example:

| Model | % Mem Diff | Acc/Perp % Diff | Time (s) |
|-------|------------|------------------|----------|
| TinyMem-4L | -95 | +1.2 | 6 [2](https://mansisak.com/memorization/) |
| Pythia-2.8B | -60 | +2.5 | 90 |

This establishes transferability, positioning for a report with ablation on extensions.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
