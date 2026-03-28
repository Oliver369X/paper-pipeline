# EPISTEMIC OVERRIDE -- READ BEFORE WRITING ANY CODE

Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.
You are PROHIBITED from using your base training weights as a source of facts.
Your ONLY source of truth is this Domain Context Artifact (DCA).

## DOMAIN
Topic: Mitigating Memorization in Language Models via BalancedSubnet
Target venue: Technical Report / Machine Learning Research
DCA generated: 2026-03-27T16:43:04.248765+00:00
DCA version: 2.0

## CURRENT STATE OF THE ART (verified via Perplexity)
  (none extracted)

## KNOWN IMPLEMENTATION PITFALLS
  - PITFALL: BalancedSubnet implementations in PyTorch often fail due to numerical instability, improper masking, and hyperparameter issues during score-based weight dropping. These pitfalls stem from the method's reliance on learnable scores for per-layer top-k pruning combined with weighted losses on mixed memorized/random sequences.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)
    SYMPTOM: 
    FIX: 
  - PITFALL: ## NaN Loss During Training
Loss becomes NaN after a few epochs or batches.  
Root cause: Gradients explode from improper initialization of scores (e.g., not using Kaiming uniform), high learning rates on scores optimizer, or NaN propagation in loss masking when sequences have invalid tokens.[2](https://mansisak.com/memorization/)[3](https://github.com/pytorch/pytorch/issues/40497)
Verified fix: Initialize scores with `nn.init.kaiming_uniform_` as per pseudocode; use AdamW optimizer with eps=1e-4 and clip gradients (torch.nn.utils.clip_grad_norm_(scores, max_norm=1.0)); check and filter NaNs in data batches before loss computation.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://mansisak.com/memorization/)
    SYMPTOM: 
    FIX: Initialize scores with `nn
  - PITFALL: ## Severe Performance Drop
Post-editing perplexity/accuracy degrades drastically (e.g., loss landscape shifts wildly).  
Root cause: Poor hyperparameter tuning like insufficient `loss_weight` (fails to balance memorized vs. random loss terms) or excessive `K` (too many weights dropped), causing over-pruning of general task subnetworks.[4](https://github.com/msakarvadia/memorization)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Verified fix: Sweep hyperparameters via grid search (e.g., loss_weight in [0.1,0.5,0.9], K=0.01-0.1 * param_size per layer); monitor validation perplexity during training and early-stop if >5% degradation, as shown effective on Pythia models.[4](https://github.com/msakarvadia/memorization)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
    SYMPTOM: 
    FIX: Sweep hyperparameters via grid search (e
  - PITFALL: ## Incomplete Memorization Removal
Model still regurgitates >20% memorized sequences after editing.  
Root cause: Inadequate shuffling or batching of memorized/random sequences, leading to biased score updates; or incorrect `drop_top_k_weights_per_layer` (not using absolute scores |s| or layer-wise top-k).[2](https://mansisak.com/memorization/)  
Verified fix: Strictly shuffle `memorized_sequences ∪ random_sequences` each epoch; implement drop as `topk_indices = torch.topk(s.abs(), k=int(K_ratio * s.numel()), largest=False); mask out those weights`; ensure 50/50 batch ratio.[2](https://mansisak.com/memorization/)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
    SYMPTOM: 
    FIX: Strictly shuffle `memorized_sequences ∪ random_sequences` each epoch; implement drop as `topk_indices = torch
  - PITFALL: ## Memory Overflow on Large Models
OOM errors during forward passes on production LMs like Pythia-6.9B.  
Root cause: No in-place restoration of original params before each drop application, or accumulating large score tensors without detaching.  
Verified fix: Copy model once (`LM_edited = copy.deepcopy(LM)`), restore params iteratively per layer in forward hook (`p.copy_(p_original)` before drop); use `torch.no_grad()` for inference checks and clear cache post-batch.[5](https://www.digitalocean.com/community/tutorials/writing-resnet-from-scratch-in-pytorch)[2](https://mansisak.com/memorization/)
    SYMPTOM: 
    FIX: Copy model once (`LM_edited = copy

## REFERENCE IMPLEMENTATIONS
  - msakarvadia/memorization (https://github.com/msakarvadia/memorization)
    KEY DECISIONS: **Name**: `mitigating-memorization` / `memorization`, **GitHub URL**: https://github.com/msakarvadia/memorization[2](https://github.com/msakarvadia/memorization)[1](https://mansisak.com/memorization/), **Star count**: **12 stars** (as of the latest page snapshot).[2](https://github.com/msakarvadia/memorization)
    DO NOT COPY: N/A
  - msakarvadia/memorization[2 (https://github.com/msakarvadia/memorization[2)
    KEY DECISIONS: **GitHub URL**: https://github.com/msakarvadia/memorization[2](https://github.com/msakarvadia/memorization)[1](https://mansisak.com/memorization/)
    DO NOT COPY: N/A
  - jbloomAus/SAELens[7 (https://github.com/jbloomAus/SAELens[7)
    KEY DECISIONS: **GitHub URL**: https://github.com/jbloomAus/SAELens[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb)
    DO NOT COPY: N/A
  - tutorials/tutorial_2_0.ipynb (https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb)
    KEY DECISIONS: **GitHub URL**: https://github.com/jbloomAus/SAELens[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb), **Star count**: ~2.5k–3.5k stars (as of recent listings; numbers fluctuate, but it is widely starred).[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb), Provides a **library for training sparse autoencoders on LLM activations**, enabling feature‑level interpretability and “intervention” pipelines that can be reused for unlearning‑style editing.[8](https://www.themoonlight.io/en/review/mitigating-memorization-in-language-models)[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb)
    DO NOT COPY: N/A
  - jbloomAus/SAELens (https://github.com/jbloomAus/SAELens)
    KEY DECISIONS: **Name**: `SAELens` (Sparse Autoencoder Lens), **GitHub URL**: https://github.com/jbloomAus/SAELens[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb), **Star count**: ~2.5k–3.5k stars (as of recent listings; numbers fluctuate, but it is widely starred).[7](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb)
    DO NOT COPY: N/A
  - huggingface/transformers (https://github.com/huggingface/transformers)
    KEY DECISIONS: No single repo, but `huggingface/transformers` is the **de facto backbone** for anyone applying BalancedSubnet‑style methods on real LLMs.[6](https://linnk.ai/insight/machine-learning/mitigating-memorization-in-language-models-comprehensive-evaluation-of-regularization-fine-tuning-and-unlearning-strategies-4e3Ifbu3/)[3](https://arxiv.org/abs/2410.02159v2)
    DO NOT COPY: N/A

## MATHEMATICAL CONSTRAINTS
  (to be populated during implementation)

## ANTI-HALLUCINATION GUARDS (CRITICAL)
The following claims are FALSE. If your code or reasoning relies on them,
STOP immediately and recheck against the DCA.
  - NEVER accept as true: 'The standard evaluation metric for 'Mitigating Memorization in Language Models via BalancedSubnet' is pixel accuracy.'
  - NEVER accept as true: 'The Transformer architecture used in 'Mitigating Memorization in Language Models via BalancedSubnet' was invented by Yann LeCun in 1998.'
  - NEVER accept as true: 'Standard practice in 'Mitigating Memorization in Language Models via BalancedSubnet' is to use a learning rate greater than 1.0.'

## QUALITY GATES (non-negotiable)
1. Every function must have a unit test (mocked tensors, no GPU required).
2. The main evaluation script MUST save results to ./outputs/metrics.json.
3. A FAILURES.md file must document what DID NOT work and why.

You are now the world-leading expert in: Mitigating Memorization in Language Models via BalancedSubnet.
Act accordingly.
