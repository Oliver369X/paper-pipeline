<!-- section=experiments generated=2026-03-27T16:29:53.986298+00:00 model=best -->

Here is a compact but rigorous experiment plan for evaluating **Mitigating Memorization in Language Models via BalancedSubnet**, including baselines, metrics, ablations, computational‑budget considerations, and a Markdown‑ready results‑table outline.

***

### Overall goal

Evaluate how well **BalancedSubnet** (BSN) mitigates memorization while preserving general‑task performance, compared to baseline mitigation strategies and ablated variants, across a controlled computational budget.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)

We assume you are either using the **TinyMem** suite or a small / medium‑scale transformer (e.g., 100M–1B parameters) for a first‑round experiment.[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)

***

### Baseline methods

Include the main classes of mitigation strategies from the paper, plus a “null” baseline.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)

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

This lets you test:  
- Is BSN clearly better than simpler unlearning / regularization?  
- How much does the “balance” term (penalizing weights important for clean data) help?  

***

### Core metrics

Design metrics along three axes: **memorization**, **utility**, and **efficiency**.[4](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)

#### 1. Memorization metrics

- **Memorized‑sequence likelihood**  
  - Per‑token loss or negative log‑likelihood on the **forget set** (memorized sequences).  
  - Compare before vs. after applying each method.  
- **Regurgitation rate**  
  - For a fixed set of “dangerous” prompts that previously elicited verbatim memorized content, measure:  
    - % of runs where model outputs ≥k tokens of the original memorized string.  
- **Security‑oriented attack metrics (optional)**  
  - Use a simple membership‑inference or extraction‑style probe if you have a small labeled dataset of memorized vs. non‑memorized examples.[5](https://linnk.ai/insight/machine-learning/mitigating-memorization-in-language-models-comprehensive-evaluation-of-regularization-fine-tuning-and-unlearning-strategies-4e3Ifbu3/)[4](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

#### 2. Utility / task performance

- **Downstream‑task accuracy**  
  - One or two held‑out tasks (e.g., classification, QA, math problem solving) not in the memorized set.  
- **Perplexity**  
  - Zero‑shot / few‑shot perplexity on a clean validation corpus. Target: minimal degradation vs. original model.[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
- **Prompt‑following fidelity**  
  - For a small benchmark of prompts, check if responses stay coherent and relevant (e.g., via human‑annotated or LLM‑based scoring).  

#### 3. Efficiency / cost

- **Wall‑clock time**  
  - Time per method (e.g., one‑pass fine‑tuning vs. Sparse‑BSN subnetwork optimization).  
- **GPU‑hours / FLOPs**  
  - For each method, log approximate GPU‑hours or gradient‑step counts.  
- **Memory footprint**  
  - Peak memory usage (original vs. edited model).  

***

### Ablation design

Inside the BSN framework, run at least these ablations to isolate the “balanced” component.[3](https://mansisak.com/memorization/)[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)

- **Subnet (no balancing)**  
  - Just the original subnet mask on the memorized set, no extra term for clean‑data importance.[3](https://mansisak.com/memorization/)[2](https://arxiv.org/html/2410.02159v2)
- **BSN (loss‑weight sweep)**  
  - Vary the `loss_weight` parameter (e.g., low, medium, high) to study the trade‑off between memorization reduction and task accuracy.[3](https://mansisak.com/memorization/)[2](https://arxiv.org/html/2410.02159v2)
- **Random mask / weak‑BSN**  
  - Random sparse mask (same sparsity as BSN) instead of optimizing via the memorized‑vs‑clean objective. Tests whether the optimization really matters.  
- **Sparsity‑level ablation**  
  - Vary `K` (number of weights pruned / dropped) to see how aggressive pruning affects memorization vs. perplexity.[2](https://arxiv.org/html/2410.02159v2)[3](https://mansisak.com/memorization/)

***

### Computational‑budget considerations

To keep experiments realistic and comparable, set a budget and constrain baselines accordingly.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)

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

***

### Suggested experiment structure

Run a single, stratified experiment across:  

- **2–3 model sizes** (e.g., small, medium).  
- **2 types of memorized content** (e.g., “noise”‑like sequences vs. backdoor‑style triggers).[2](https://arxiv.org/html/2410.02159v2)[1](https://arxiv.org/abs/2410.02159v2)
- **2–3 training‑time checkpoints** (early, mid, late) to see how memorization‑mitigation interacts with training dynamics.[1](https://arxiv.org/abs/2410.02159v2)[2](https://arxiv.org/html/2410.02159v2)

For each cell in this grid, run:  
- Original model.  
- All baselines (1–5 above).  
- BSN + key ablations (Subnet, multiple `loss_weight`, 1–2 sparsity levels).  

***

### Results‑table outline (Markdown)

You can then collapse this into per‑setting tables or concatenate into one large table. Here is a generic outline per model‑size‑and‑data‑type configuration.

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

You can then produce:

- One table **per model size** (e.g., 100M, 300M).  
- One table **per memorized content type** (noise vs. backdoor).  
- One table **per training‑time checkpoint**.  

***

If you tell me your **target model size** (e.g., 125M, 700M, etc.) and whether you plan to run on **TinyMem** or your own dataset, I can draft a concrete parameter grid (learning rates, epochs, `K`, `loss_weight` values) and a step‑by‑step script‑level experiment plan for you.
