# EPISTEMIC OVERRIDE -- READ BEFORE WRITING ANY CODE

Your pre-training knowledge is OUTDATED and UNRELIABLE for this domain.
You are PROHIBITED from using your base training weights as a source of facts.
Your ONLY source of truth is this Domain Context Artifact (DCA).

## DOMAIN
Topic: Research topic
Target venue: generic venue
DCA generated: 2026-03-26T20:59:14.403962+00:00
DCA version: 2.0

## CURRENT STATE OF THE ART (verified via Perplexity)
  - **Title, authors, year**
  - **Key technical finding**
  - **Main mathematical contribution**, and
  - a *generic* venue label (e.g., “arXiv‑first, generic‑AI‑venue‑level”).[2](https://arxiv.org/abs/2412.12121)
  - **Authors:** A. Grattafiori et al. (Meta) [arXiv:2407.21783][4](https://arxiv.org/abs/2407.21783)[2](https://arxiv.org/abs/2412.12121)
  - **Year:** 2024 (v3 Nov 2024)
  - **Key technical finding:** Introduces a “herd” of open‑weight Llama‑3 language models (up to 405B parameters) with strong multilingual, coding, reasoning, and tool‑use capabilities; balances performance vs. openness.[2](https://arxiv.org/abs/2412.12121)[4](https://arxiv.org/abs/2407.21783)
  - **Mathematical contribution:** Systematic ablation of scaling laws (parameter count, data mix, training compute) and evaluation protocols for foundation‑model quality; empirical characterization of “good” post‑train configurations.[4](https://arxiv.org/abs/2407.21783)[2](https://arxiv.org/abs/2412.12121)
  - **Venue level:** arXiv‑first, generic‑AI‑venue‑level (cs.AI/cs.CL).[2](https://arxiv.org/abs/2412.12121)
  - **Authors:** Alibaba Tongyi Lab et al. [arXiv:2407.10671][2](https://arxiv.org/abs/2412.12121)
  - **Year:** 2024
  - **Key technical finding:** Presents **Qwen2**, a family of open‑source, multilingual LLMs with strong performance on code, math, and reasoning, while remaining licensable and inspectable.[2](https://arxiv.org/abs/2412.12121)
  - **Mathematical contribution:** Analysis of data‑scaling and model‑scaling curves for multilingual quality; empirical justification of curriculum‑style data mixing across language and code domains.[2](https://arxiv.org/abs/2412.12121)
  - **Venue level:** arXiv‑first, generic‑AI‑venue‑level (cs.CL).[2](https://arxiv.org/abs/2412.12121)
  - **Authors:** Google DeepMind et al. [arXiv:2403.05530][2](https://arxiv.org/abs/2412.12121)

## KNOWN IMPLEMENTATION PITFALLS
  - PITFALL: **Symptom**: Training loss quickly becomes `NaN` or jumps to very large values (e.g., 1e6+) in the first few steps.[4](https://www.dawsondean.com/PytorchDebugging.htm)[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Learning rate too high.
    SYMPTOM: 
    FIX: 
  - PITFALL: Poor initialization (e.g., very large weights, or no initialization at all).
    SYMPTOM: 
    FIX: 
  - PITFALL: Unstable loss function (e.g., `log` on inputs that can be ≤0, or masking that propagates `NaN` gradients).[5](https://github.com/pytorch/pytorch/issues/121416)[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)[6](https://intellipaat.com/blog/deep-learning-nan-loss-reasons/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Reduce learning rate significantly (often 1–2 orders of magnitude lower).
    SYMPTOM: 
    FIX: 
  - PITFALL: Use standard initialization (`torch.nn.init.kaiming_normal_`, `xavier_normal`, etc.).
    SYMPTOM: 
    FIX: 
  - PITFALL: Avoid numerically fragile patterns such as `torch.log` on raw logits; prefer log‑sum‑exp or `nn.LogSoftmax` + `NLLLoss` or `nn.CrossEntropyLoss` directly.[7](https://www.33rdsquare.com/pytorch-a-comprehensive-guide-to-common-mistakes/)[8](https://discuss.pytorch.org/t/loss-is-nan-vanishing-exploding-gradients/162130)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Loss plateaus immediately, gradients are exactly zero, or `model.parameters()` barely change after many steps.[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)[10](https://docs.pytorch.org/rl/main/reference/generated/knowledge_base/PRO-TIPS.html)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Forgetting `optimizer.zero_grad()` inside the training loop, so gradients accumulate from previous iterations.
    SYMPTOM: 
    FIX: 
  - PITFALL: Accidentally detaching the graph (e.g., `.detach()` or `.data` on the parameter tensors).
    SYMPTOM: 
    FIX: 
  - PITFALL: Passing the wrong tensor into the loss (e.g., using `prediction.detach()` instead of `prediction`).[10](https://docs.pytorch.org/rl/main/reference/generated/knowledge_base/PRO-TIPS.html)[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Always wrap the training step with:
    SYMPTOM: 
    FIX: 
  - PITFALL: Avoid inplace mutations and `.data`/`.detach()` on things that should be trainable.[10](https://docs.pytorch.org/rl/main/reference/generated/knowledge_base/PRO-TIPS.html)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: `RuntimeError: size mismatch`, `mat1 and mat2 shapes cannot be multiplied`, or similar shape‑related errors during forward/backward.[13](https://www.byteplus.com/en/topic/401878)[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: size mismatch`, `mat1 and mat2 shapes cannot be multiplied`, or similar shape‑related errors during forward/backward
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Incorrect layer parameterization (e.g., `nn.Linear(in_features=10)` but upstream convolution outputs  `batch × 16 × 32 × 32` and is passed directly without `flatten`).
    SYMPTOM: 
    FIX: 
  - PITFALL: Mismatched image/channel order (`C × H × W` vs `H × W × C`) baked into a `__getitem__` or `DataLoader`.[14](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/common-pytorch-pitfalls)[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Always print intermediate shapes inside the model and inspect them with a tiny dummy input:
    SYMPTOM: 
    FIX: 
  - PITFALL: Use `nn.Flatten` or explicit `.view()` with correct size (computed from the conv output) rather than hard‑coding `in_features`.[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Loss starts at a very high value and does not meaningfully improve, or model outputs “garbage” probabilities (e.g., all‑zeros logit vectors capped at 1 after `softmax`).[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)[4](https://www.dawsondean.com/PytorchDebugging.htm)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Using `MSELoss` for classification indices instead of `CrossEntropyLoss`.
    SYMPTOM: 
    FIX: 
  - PITFALL: Using integer‑class labels with `BCELoss` instead of `BCEWithLogitsLoss`.
    SYMPTOM: 
    FIX: 
  - PITFALL: Applying `nn.Softmax` then `CrossEntropyLoss`, which is numerically unstable and ignores the logits’ gradient structure.[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: For classification with integer labels: use `nn.CrossEntropyLoss` on raw logits, no `softmax` beforehand.[8](https://discuss.pytorch.org/t/loss-is-nan-vanishing-exploding-gradients/162130)[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)
    SYMPTOM: 
    FIX: 
  - PITFALL: For multi‑label or binary classification: use `BCEWithLogitsLoss` on logits, not `BCELoss` on already‑squeezed probabilities.[7](https://www.33rdsquare.com/pytorch-a-comprehensive-guide-to-common-mistakes/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Early‑layer gradients are near zero (vanishing), or gradients suddenly jump to huge values and then `NaN`.[6](https://intellipaat.com/blog/deep-learning-nan-loss-reasons/)[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Unstable or improperly clipped gradients in long sequences or deep stacks (e.g., self‑attention or RNN‑style modules reimplemented from scratch).
    SYMPTOM: 
    FIX: 
  - PITFALL: Absence of proper initialization or normalization (no `LayerNorm`, bad attention scores without scaling).
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Clip gradients by norm:
    SYMPTOM: 
    FIX: 
  - PITFALL: Use standard, well‑tested modules (e.g., `nn.MultiheadAttention` instead of home‑grown multi‑head) when possible, and scale attention scores by `1/sqrt(d_k)`.[15](https://stackoverflow.com/questions/79027142/exploding-gradient-nan-training-loss-and-validation-loss-in-multi-head-self-at)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Sudden `NaN` or flat‑out wrong outputs; or “cannot be multiplied on CUDA” errors when the model is on GPU but data is on CPU.[16](https://www.youtube.com/watch?v=szmXqtaXSWE)[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Mixing `torch.float32` and `torch.int64` (e.g., `CrossEntropyLoss` with float labels).
    SYMPTOM: 
    FIX: 
  - PITFALL: Forgetting to move data to the same device as the model (`model.cuda()` but input on CPU).
    SYMPTOM: 
    FIX: 
  - PITFALL: Incorrect normalization or augmentation (e.g., clipping ranges, augmenting labels in the wrong order).[16](https://www.youtube.com/watch?v=szmXqtaXSWE)[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Always align device and dtype at the inner loop:
    SYMPTOM: 
    FIX: 
  - PITFALL: Normalize data to the same range as the model was designed for (e.g., imagenet normalization for pretrained CNNs) and avoid inplace augmentations that mutate the same tensor across workers.[7](https://www.33rdsquare.com/pytorch-a-comprehensive-guide-to-common-mistakes/)[11](https://www.learnpytorch.io/pytorch_most_common_errors/)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Performance on validation drops, or results are noisy even though training loss is low; sometimes `NaN` during validation if dropout or batch‑norm is misconfigured.[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)[3](https://apxml.com/courses/getting-started-with-pytorch/chapter-8-monitoring-debugging-models/inspecting-gradients-issues)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Forgetting `model.train()` vs `model.eval()` around training and validation loops.
    SYMPTOM: 
    FIX: 
  - PITFALL: Not using `torch.no_grad()` in inference, which can cause memory blow‑ups and subtle numerical issues under heavy load.[16](https://www.youtube.com/watch?v=szmXqtaXSWE)[9](https://www.youtube.com/watch?v=O2wJ3tkc-TU)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Wrap training and eval loops properly:
    SYMPTOM: 
    FIX: 
  - PITFALL: **Symptom**: Reported metrics look good but cannot be reproduced; or the “novel” module has no gradient or is effectively identity‑like.[2](https://arxiv.org/pdf/2307.13777.pdf)[1](https://das.encs.concordia.ca/pdf/ho2023empirical.pdf)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Root cause**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Wrong implementation of the algorithm (e.g., incorrect masking, normalization, or per‑sample weighting) classified as “wrong algorithm implementation” in an empirical study of PyTorch bugs.[17](https://arxiv.org/abs/2307.13777v1)[2](https://arxiv.org/pdf/2307.13777.pdf)
    SYMPTOM: 
    FIX: 
  - PITFALL: Accidentally breaking the computation graph (e.g., converting to NumPy, then back to tensor, or using `@torch.no_grad()` in the middle of an update step)..[1](https://das.encs.concordia.ca/pdf/ho2023empirical.pdf)[2](https://arxiv.org/pdf/2307.13777.pdf)
    SYMPTOM: 
    FIX: 
  - PITFALL: **Verified fix**:
    SYMPTOM: 
    FIX: 
  - PITFALL: Add unit tests for the model’s gradient flow on small synthetic data (gradient ≠ zero, parameter stats change after a step).
    SYMPTOM: 
    FIX: 
  - PITFALL: Match the implementation to the paper’s pseudocode or known‑correct reference (e.g., official library implementations or well‑tested repos like `PyTorch‑Research‑Paper‑Implementations`).[18](https://github.com/cjfghk5697/Pytorch-Research-Paper-Implementations)[17](https://arxiv.org/abs/2307.13777v1)
    SYMPTOM: 
    FIX: 

## REFERENCE IMPLEMENTATIONS
  - topics/sparse-autoencoders (https://github.com/topics/sparse-autoencoders)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - koayon/awesome-sparse-autoencoders (https://github.com/koayon/awesome-sparse-autoencoders)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - jbloomAus/SAELens (https://github.com/jbloomAus/SAELens)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - saelens/SKILL.md (https://github.com/zechenzhangAGI/AI-research-SKILLs/blob/main/04-mechanistic-interpretability/saelens/SKILL.md)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - EleutherAI/sparsify (https://github.com/EleutherAI/sparsify)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - ai-safety-foundation/sparse_autoencoder (https://github.com/ai-safety-foundation/sparse_autoencoder)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - neelnanda-io/TransformerLens (https://github.com/neelnanda-io/TransformerLens)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - ayyucekizrak/Mechanistic-Interpretability (https://github.com/ayyucekizrak/Mechanistic-Interpretability)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - neelnanda-io/sae-dashboard (https://github.com/neelnanda-io/sae-dashboard)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A
  - neelnanda-io/1L-Sparse-Autoencoder (https://github.com/neelnanda-io/1L-Sparse-Autoencoder)
    KEY DECISIONS: N/A
    DO NOT COPY: N/A

## MATHEMATICAL CONSTRAINTS
  (to be populated during implementation)

## ANTI-HALLUCINATION GUARDS (CRITICAL)
The following claims are FALSE. If your code or reasoning relies on them,
STOP immediately and recheck against the DCA.
  - NEVER accept as true: 'The standard evaluation metric for 'Research topic' is pixel accuracy.'
  - NEVER accept as true: 'The Transformer architecture used in 'Research topic' was invented by Yann LeCun in 1998.'
  - NEVER accept as true: 'Standard practice in 'Research topic' is to use a learning rate greater than 1.0.'

## COMPUTE DELEGATION (MANDATORY)
The experiment requires ~16.0 GB GPU memory.
YOU MUST delegate GPU-intensive work to Colab MCP (A100 accelerator).
DO NOT attempt to run GPU-intensive code locally.

## QUALITY GATES (non-negotiable)
1. Every function must have a unit test (mocked tensors, no GPU required).
2. The main evaluation script MUST save results to ./outputs/metrics.json.
3. A FAILURES.md file must document what DID NOT work and why.

You are now the world-leading expert in: Research topic.
Act accordingly.
