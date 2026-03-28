<!-- section=methodology generated=2026-03-27T18:07:15.101416+00:00 model=best -->

**K-FAC-based curvature editing offers a promising, data-efficient way to reduce memorization in small language models (SLMs) by targeting low-curvature directions in the loss landscape, extending ideas from arXiv:2510.24256 to resource-constrained settings.**[1](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/pdf/2510.24256.pdf)

This methodology adapts the paper's K-FAC decomposition to SLMs like Phi-3-mini (3.8B parameters), focusing on feasibility for your AI safety research at YAIS Lab.[3](https://huggingface.co/blog/jjokah/small-language-model)[4](https://encord.com/blog/microsoft-phi-3-small-language-model/)

## Problem Formulation

Memorization in SLMs occurs when models regurgitate training sequences verbatim, quantified by prefix-suffix exact match under greedy decoding: for prompt $$P$$ and target $$S$$, compute Levenshtein distance $$d(\hat{S}, S)$$ where $$\hat{S}$$ is generated output.[2](https://arxiv.org/pdf/2510.24256.pdf)[5](https://mansisak.com/memorization/)

High per-example loss curvature links to brittle memorization, but aggregate dataset curvature reveals low-curvature directions (flatter basins) correspond to rarely used, memorization-heavy weights.[2](https://arxiv.org/pdf/2510.24256.pdf)

Objective: Decompose MLP weights via K-FAC-approximated Fisher Information Matrix (FIM) $$\mathbf{F} \approx \mathbf{G} \otimes \mathbf{A}$$, where $$\mathbf{G} = \mathbb{E}[\mathbf{g}\mathbf{g}^\top]$$ (gradients) and $$\mathbf{A} = \mathbb{E}[\mathbf{a}\mathbf{a}^\top]$$ (activations), then prune low-curvature components to suppress recitation while preserving perplexity and reasoning.[6](https://github.com/n-gao/pytorch-kfac)[2](https://arxiv.org/pdf/2510.24256.pdf)

## Baselines

Compare against three classes from memorization mitigation literature, scaled to SLMs:[5](https://mansisak.com/memorization/)[7](https://arxiv.org/html/2410.02159)

| Method          | Description                          | Pros/Cons for SLMs                  |
|-----------------|--------------------------------------|-------------------------------------|
| Regularizers   | Add loss curvature penalties (e.g., SAM) during fine-tuning. [5](https://mansisak.com/memorization/) | Slow, ineffective on compute-limited SLMs. |
| Fine-tuning    | SFT/RLHF on retain set post-forget. [5](https://mansisak.com/memorization/) | Effective but expensive for SLMs. |
| Unlearning (BSN) | Train binary mask to maximize forget loss vs. retain. [2](https://arxiv.org/pdf/2510.24256.pdf) | Strong targeted suppression; requires labeled forget set unlike K-FAC. [2](https://arxiv.org/pdf/2510.24256.pdf) |

Use SVD truncation (prune low singular values) as data-free ablation.[2](https://arxiv.org/pdf/2510.24256.pdf)

## Proposed Method Outline

1. **Collect Statistics**: Stream ~1-5M tokens from SLM pretraining mix (e.g., FineMath + Dolma subset) through target SLM (Phi-3-mini). Buffer pre-MLP activations $$\mathbf{a}$$ (forward) and gradients $$\mathbf{g}$$ (backward under NLL). Compute $$\mathbf{A}, \mathbf{G}$$ per MLP layer.[3](https://huggingface.co/blog/jjokah/small-language-model)[2](https://arxiv.org/pdf/2510.24256.pdf)

2. **K-FAC Decomposition**: Eigendecompose $$\mathbf{G} = U_G \Lambda_G U_G^\top$$, $$\mathbf{A} = U_A \Lambda_A U_A^\top$$. For weight $$W \in \mathbb{R}^{p \times q}$$, project $$C = U_G^\top W U_A$$, sort pairs $$(i,j)$$ by curvature mass $$\Pi_{ij} = \lambda_i^G \mu_j^A$$. Retain top-$$\rho=60\%$$ mass pairs via mask $$M$$, reconstruct $$W' = U_G (C \odot M) U_A^\top$$.[6](https://github.com/n-gao/pytorch-kfac)[2](https://arxiv.org/pdf/2510.24256.pdf)

3. **Edit & Tune**: Apply to late MLP layers (e.g., 80% from end, as in OLMo edits). Sweep $$\rho$$, layers (0.1% compute via small labeled forget set). No retraining needed, unlike BSN.[2](https://arxiv.org/pdf/2510.24256.pdf)

4. **Evaluation**: Test on held-out memorized sequences (e.g., Dolma val, quotes), compute strict/loose accuracy, avg. Levenshtein. Track perplexity, MMLU-Pro Math, logic (e.g., Boar Etruscan).[2](https://arxiv.org/pdf/2510.24256.pdf)

Implement via PyTorch KFAC repo; fits Colab for SLMs.[6](https://github.com/n-gao/pytorch-kfac)

## Minimal Viable Result

Success if K-FAC edit on Phi-3-mini reduces strict recitation accuracy by >80% on unseen memorized set (e.g., historical quotes: <20% from 99%), outperforms BSN/SVD on OOD memorization while $$\Delta$$PPL <2 and logic retention >90%.[4](https://encord.com/blog/microsoft-phi-3-small-language-model/)[2](https://arxiv.org/pdf/2510.24256.pdf)

Demonstrate spectrum: memorization/math drop most, reasoning robust. This replicates/extends arXiv:2510.24256 to SLMs, enabling arXiv submission with ablation on 1-4B models.[3](https://huggingface.co/blog/jjokah/small-language-model)[2](https://arxiv.org/pdf/2510.24256.pdf)

What SLM (e.g., Phi-3-mini or SmolLM-1.7B) and dataset access do you have?[8](https://www.secondtalent.com/resources/best-small-language-models-slms-with-open-source-development/)[3](https://huggingface.co/blog/jjokah/small-language-model)
