# Draft: Mitigating Memorization in Language Models via BalancedSubnet

**Target venue / reference:** Technical Report / Machine Learning Research

*Disclaimer: borrador asistido por LLM (Perplexity); no sustituye experimentos ejecutados, números reproducibles ni revisión por pares. Ver `docs/MODE_NARRATIVE_VS_EMPIRICAL.md` y `docs/ARXIV_TARGET_ALIGNMENT.md` en el repositorio.*

*Generated 2026-03-27T16:43:48.749554+00:00 UTC*

## methodology



BalancedSubnet effectively mitigates memorization in language models by pruning weights responsible for regurgitating training data while preserving general performance. This methodology investigates improvements to it, targeting a technical report or ML research venue like arXiv or NeurIPS workshops.[12](https://mansisak.com/memorization/)

## Problem Formulation

Memorization occurs when a language model (LM) encodes training sequences in its weights, enabling verbatim regurgitation upon prompting with prefixes, as defined by (n,k)-memorization where the first k tokens elicit the remaining n-k tokens via greedy decoding.[21](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Formally, for an LM $$ M $$ and artifact set $$ s_A $$ (e.g., noised or backdoored sequences from training data $$ D $$), measure % Memorized as $$\frac{ \text{ elicited artifacts}}{ \text{ total artifacts}} \times 100$$, where artifacts are perturbations like noise ($$ s_n $$ with ±1 shifts) or backdoors (triggered sequences).[12](https://mansisak.com/memorization/)
The goal is to edit $$ M $$ post-training to minimize % Memorized on $$ s_A $$ (target: -100% change) while keeping test accuracy/perplexity near baseline (0% change).[21](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Baselines

Compare against three classes from prior work:[12](https://mansisak.com/memorization/)

- **Regularizers** (train-time): Spectral norm, loss truncation, example-tied dropout—slow, often fail to curb memorization without hurting convergence.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
- **Fine-tuning** (post-training): On clean data, extra data, or both—effective but computationally expensive (e.g., 3600s vs. unlearning's <100s).[2](https://mansisak.com/memorization/)
- **Unlearning** (post-training, weight/neuron-based): Greedy, Durable, Subnet, neuron methods (e.g., Hard Concrete, Integrated Gradients)—BalancedSubnet outperforms by balancing memorization removal and performance preservation across model sizes/data types.[21](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Proposed Method Outline

**Core: Implement/Extend BalancedSubnet.** Start with the official GitHub code for TinyMem/Pythia models.[32](https://mansisak.com/memorization/)

1. Train baseline TinyMem LMs (2-16 layers, math/language tasks) with artifacts (5-10% noise/backdoors) until memorization emerges (~epochs 50-3500).[2](https://mansisak.com/memorization/)
2. Apply BalancedSubnet: Initialize per-parameter scores (Kaiming uniform), optimize binary mask via straight-through estimator on shuffled memorized + random sequences; loss = LM loss × batch_mask where mask penalizes memorized (-(1-weight)) vs. random (+weight) sequences; drop top-K weights per layer.[2](https://mansisak.com/memorization/)
3. **Novel Extension (for investigation):** Add interpretability—use activation gradients or SAEs to validate pruned subnetworks target memorization circuits; test adaptive K via loss curvature; scale to Gemma-2B with Bolivia-specific data (e.g., local texts) for regional relevance.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)







&nbsp;

&nbsp;





&nbsp;

---





&nbsp;

---





1. **No mitigation**
  - Original model, no edits.
2. **Regularizer‑based**
  - E.g., **LoRA‑reg** or other regularization methods used in the paper.[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
3. **Fine‑tuning‑based**
  - Standard “re‑fine‑tune while down‑weighting / excluding memorized data”.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)
4. **Unlearning‑based (non‑BSN)**
  - At least 2–3 published unlearning methods (e.g., **Subnet**, **Scrubby**, other binary‑mask or gradient‑based unlearning baselines available in the codebase).[3](https://mansisak.com/memorization/)[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
5. **BalancedSubnet** (your target method)
  - With your own hyperparameter tuning.



- Is BSN clearly better than simpler unlearning / regularization?  
- How much does the “balance” term (penalizing weights important for clean data) help?

---







- **Memorized‑sequence likelihood**  
  - Per‑token loss or negative log‑likelihood on the **forget set** (memorized sequences).  
  - Compare before vs. after applying each method.
- **Regurgitation rate**  
  - For a fixed set of “dangerous” prompts that previously elicited verbatim memorized content, measure:  
    - % of runs where model outputs ≥k tokens of the original memorized string.
- **Security‑oriented attack metrics (optional)**  
  - Use a simple membership‑inference or extraction‑style probe if you have a small labeled dataset of memorized vs. non‑memorized examples.[5](https://linnk.ai/insight/machine-learning/mitigating-memorization-in-language-models-comprehensive-evaluation-of-regularization-fine-tuning-and-unlearning-strategies-4e3Ifbu3/)[4](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)



- **Downstream‑task accuracy**  
  - One or two held‑out tasks (e.g., classification, QA, math problem solving) not in the memorized set.
- **Perplexity**  
  - Zero‑shot / few‑shot perplexity on a clean validation corpus. Target: minimal degradation vs. original model.[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
- **Prompt‑following fidelity**  
  - For a small benchmark of prompts, check if responses stay coherent and relevant (e.g., via human‑annotated or LLM‑based scoring).



- **Wall‑clock time**  
  - Time per method (e.g., one‑pass fine‑tuning vs. Sparse‑BSN subnetwork optimization).
- **GPU‑hours / FLOPs**  
  - For each method, log approximate GPU‑hours or gradient‑step counts.
- **Memory footprint**  
  - Peak memory usage (original vs. edited model).

---





- **Subnet (no balancing)**  
  - Just the original subnet mask on the memorized set, no extra term for clean‑data importance.[3](https://mansisak.com/memorization/)[2](https://arxiv.org/html/2410.02159v2)
- **BSN (loss‑weight sweep)**  
  - Vary the `loss_weight` parameter (e.g., low, medium, high) to study the trade‑off between memorization reduction and task accuracy.[3](https://mansisak.com/memorization/)[2](https://arxiv.org/html/2410.02159v2)
- **Random mask / weak‑BSN**  
  - Random sparse mask (same sparsity as BSN) instead of optimizing via the memorized‑vs‑clean objective. Tests whether the optimization really matters.
- **Sparsity‑level ablation**  
  - Vary `K` (number of weights pruned / dropped) to see how aggressive pruning affects memorization vs. perplexity.[2](https://arxiv.org/html/2410.02159v2)[3](https://mansisak.com/memorization/)

---





- **Model class**  
  - Pick one small transformer (e.g., 100M–300M) or a TinyMem model as the main testbed.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)
- **Total GPU‑hour cap**  
  - Example: 100 GPU‑hours per method (adjust depending on your cluster).  
  - For fine‑tuning‑based baselines, use early‑stopping or fewer epochs if they exceed this.
- **Per‑run limits**  
  - Wall‑time: 12–24 hours max per condition.  
  - Hyperparameters:  
    - Limit grid search (e.g., 2–3 learning rates, 1–3 epochs for fine‑tuning, 2–3 `K`/`loss_weight` values for BSN).
- **Checkpointing**  
  - Save only the best‑performing checkpoint per method to avoid over‑fitting to the evaluation set.

---





- **2–3 model sizes** (e.g., small, medium).  
- **2 types of memorized content** (e.g., “noise”‑like sequences vs. backdoor‑style triggers).[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
- **2–3 training‑time checkpoints** (early, mid, late) to see how memorization‑mitigation interacts with training dynamics.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)



- Original model.  
- All baselines (1–5 above).  
- BSN + key ablations (Subnet, multiple `loss_weight`, 1–2 sparsity levels).

---





```markdown
| Method              | Memorized‑loss ↑ | Regurg. rate ↓ | PPL‑clean (Δ) | Task‑acc (Δ) | GPU‑hours | Notes |
|---------------------|------------------|----------------|---------------|--------------|-----------|-------|
| Original            | 0.00             | 1.00           | 0.00          | 0.00         | 0.0       | -     |
| Reg‑based (LoRA‑reg)| +0.15            | 0.85           | +0.05         | -0.03        | 12.0      | full‑fine‑tune |
| FT‑based            | +0.30            | 0.45           | +0.12         | -0.08        | 25.0      | 3 epochs |
| Subnet              | +0.40            | 0.30           | +0.08         | -0.05        | 8.0       | no balance |
| Subnet‑low‑λ        | +0.45            | 0.20           | +0.10         | -0.07        | 8.0       | low loss_weight |
| Subnet‑high‑λ       | +0.48            | 0.18           | +0.15         | -0.12        | 8.0       | high loss_weight |
| BSN (best‑λ)        | +0.52            | 0.12           | +0.09         | -0.04        | 9.0       | tuned λ |
| Random‑mask         | +0.10            | 0.90           | +0.02         | -0.01        | 7.5       | same sparsity |
```

- **↑** = higher is better (memorization reduction).  
- **↓** = lower is better (memorization / regurgitation).  
- **Δ** = absolute or relative change vs. original.



- One table **per model size** (e.g., 100M, 300M).  
- One table **per memorized content type** (noise vs. backdoor).  
- One table **per training‑time checkpoint**.

---



&nbsp;





&nbsp;



- **Scaling to massive models (>10B params):** Tested only up to Pythia-6.9B; lacks evaluation on frontier LLMs where subnet localization may degrade due to parameter scale.[2](https://arxiv.org/abs/2410.02159v2)
- **Long-context memorization:** Focuses on short synthetic sequences; untested on real-world long-context regurgitation in extended prompting regimes.
- **Adversarial extraction attacks:** No assessment against advanced membership inference or extraction attacks post-unlearning, risking residual leakage.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
- **Multi-modal models:** Limited to text-only GPT-2-style architectures; applicability to vision-language or audio models undemonstrated.
- **Mechanistic interpretability:** Pruning lacks causal analysis of excised circuits; unclear if it targets true memorization mechanisms vs. proxies.[3](https://mansisak.com/memorization/)
- **Efficiency in continual unlearning:** Single-shot only; no streaming or repeated unlearning for dynamic forget sets, critical for production.
- **Real memorized data diversity:** Relies on synthetic noise/backdoors; gaps in copyrighted, PII, or multilingual real extracts from Pile/C4.[2](https://arxiv.org/abs/2410.02159v2)
- **Theoretical guarantees:** Empirical balancing term unproven; lacks bounds on utility-memorization trade-off or approximation error.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)







&nbsp;

&nbsp;





- Math sequence models (additive/multiplicative synthetic sequences with noise/backdoor artifacts). 
- Toy language models (Wikipedia corpus with noise/backdoor artifacts). 
Production validation uses Pythia models (2.8B and 6.9B parameters, trained on The Pile).[1](https://arxiv.org/abs/2410.02159v2)









&nbsp;





&nbsp;





&nbsp;











&nbsp;





&nbsp;

---



- **URL**: https://github.com/msakarvadia/memorization[1](https://github.com/msakarvadia/memorization)[2](https://github.com/msakarvadia/memorization/blob/main/README.md)
- **License**: MIT[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Repository created in 2024; last commit logs and issue activity indicate active development through at least early 2025.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Reference implementation of **BalancedSubnet** and other unlearning‑based memorization‑mitigation methods; includes TinyMem models and scripts for applying BalancedSubnet to both toy and Pythia‑scale LMs.[3](https://arxiv.org/abs/2410.02159v2)[4](https://arxiv.org/html/2410.02159v1)[1](https://github.com/msakarvadia/memorization)

---



- **URL**: `memorization/localize/weight/` and `localize_memorization.py` / `prod_grad.py` in the same repo[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **License**: MIT (same as above)[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Subdirectory code and scripts updated in line with the main repo; last‑run CSVs and notebooks indicate experiments through 2025.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Contains the core **BalancedSubnet weight‑level unlearning** implementation (learnable binary mask + dual‑objective loss) and Pythia‑compatible unlearning scripts, making it the closest reference‑implementation for your own BalancedSubnet experiments.[4](https://arxiv.org/html/2410.02159v1)[3](https://arxiv.org/abs/2410.02159v2)[1](https://github.com/msakarvadia/memorization)

---



- **URL**: `memorization/vis/` and ` Visualization_Notebook.ipynb` / `pythia_unlearning_results.ipynb` in the same repo[1](https://github.com/msakarvadia/memorization)[2](https://github.com/msakarvadia/memorization/blob/main/README.md)
- **License**: MIT[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Jupyter notebooks and CSVs were last updated in 2025, with full Pythia unlearning runs and “best runs” CSVs.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Provides a ready setup for **visualizing BalancedSubnet edits** (e.g., loss landscapes before/after) and reproducing the paper’s Pythia 2.8B/6.9B experiments.[3](https://arxiv.org/abs/2410.02159v2)[4](https://arxiv.org/html/2410.02159v1)[1](https://github.com/msakarvadia/memorization)

---



- **URL**: https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **License**: Not a full BalancedSubnet codebase; likely refers to internal or separate code, but explicitly cites BalancedSubnet as a baseline.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **Last‑update signal**: Published blog/research note in late 2025.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **Relevance**: Conceptual reference that **uses BalancedSubnet (BSN)** as an SOTA unlearning baseline for evaluating memorization via loss‑curvature, useful if you want to compare or extend BalancedSubnet‑style masking.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

---



&nbsp;





&nbsp;





















&nbsp;













&nbsp;





&nbsp;

---



&nbsp;

&nbsp;

---



&nbsp;