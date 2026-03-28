<!-- section=methodology generated=2026-03-24T02:22:58.916076+00:00 model=claude-sonnet-4.6-thinking -->

Here is a concrete, end-to-end methodology for a **research-and-build** project that targets a generic CS/AI/systems venue (arXiv, workshops, ACL Findings, EMNLP, etc.) with a paired GitHub repository.

***

## Problem Formulation

The first task is converting a vague interest into a falsifiable, scoped claim. A good problem formulation has three components:[1](https://deeplearning.cs.cmu.edu/F23/document/recitation/Recitation7/Paper_Writing_Workshop.pdf)

- **Gap statement**: "Existing approach X works well for Y, but fails at Z because of limitation L." Ground this in 5–10 related papers via Google Scholar and Papers With Code.
- **Research question (RQ)**: A single, testable sentence — e.g., *"Can method M reduce L by ≥K% on benchmark B without sacrificing performance on Y?"*
- **Scope constraints**: Fix the input/output format, the domain, and any compute budget. This prevents scope creep and makes the GitHub artifact well-defined.[2](https://arxiv.org/html/2410.03205v1)

Write the problem formulation as a one-page document *before* writing any code — this becomes your paper's Introduction and §2.

***

## Baseline Selection

Baselines are the backbone of credibility. Select at minimum three tiers:[1](https://deeplearning.cs.cmu.edu/F23/document/recitation/Recitation7/Paper_Writing_Workshop.pdf)

| Tier | Type | Purpose |
|---|---|---|
| **Trivial baseline** | Random, majority-class, or rule-based | Proves the task is non-trivial |
| **Standard baseline** | Best published method on the same benchmark | Establishes competitive context |
| **Ablated version of your method** | Your full method minus one key component | Isolates contribution causally |

For each baseline, pin an exact commit or model checkpoint in your GitHub repo so results are reproducible. Use a `baselines/` folder with one script per method and a shared `evaluate.py`.[3](https://pmc.ncbi.nlm.nih.gov/articles/PMC11828340/)[4](https://www.linkedin.com/pulse/boosting-research-reproducibility-best-practices-data-bir%C3%B3-phd--ykm0f)

***

## Proposed Method Outline

Structure your method as an *incremental improvement* over the standard baseline — not a full redesign. A practical four-step pipeline:[5](https://benjaminnoble.org/blog/minumum-viable-paper)

1. **Formalize inputs/outputs**: Define data schema, splits (train/val/test), and the metric function. Commit this as `data/schema.json` and `metrics.py` on Day 1.
2. **Implement a skeleton**: A minimal, runnable version of your idea — often fewer than 200 lines. No tuning yet.
3. **Identify the core mechanism**: One algorithmic choice that differentiates your method (e.g., a different loss function, retrieval step, attention pattern). This becomes your *contribution claim*.
4. **Iterative refinement loop**: Run → measure → identify largest error mode → patch → repeat. Each loop should be completable in under a day.[5](https://benjaminnoble.org/blog/minumum-viable-paper)

For systems/ML papers, the GitHub repo should include: `README.md` (quickstart in < 5 commands), `environment.yml` or `Dockerfile`, `train.py`, `evaluate.py`, and a `results/` folder with pre-populated CSV tables.[3](https://pmc.ncbi.nlm.nih.gov/articles/PMC11828340/)

***

## Paper Structure Path

Map your build artifacts directly to paper sections:[6](https://theaiinternship.com/blog/ai-research-publication-guide-2025/)

- `schema.json` + EDA notebook → §3 Dataset
- `baselines/` scripts + results → §4.1 Baselines
- core mechanism code → §4.2 Proposed Method
- `evaluate.py` + `results/*.csv` → §5 Experiments
- ablation script → §5.3 Ablation Study

This tight coupling between code and paper means you write the paper *as* you build, not after.[5](https://benjaminnoble.org/blog/minumum-viable-paper)

***

## Minimal Viable Result (MVR)

An MVR is the weakest possible result that still justifies a submission. You need **all four** of the following:[7](https://www.userinterviews.com/blog/minimum-viable-research-practical-guide)[5](https://benjaminnoble.org/blog/minumum-viable-paper)

- **Quantitative improvement**: Your method beats the standard baseline on at least one metric by a margin larger than the standard deviation across 3 random seeds.
- **Causal evidence**: Your ablation shows the core mechanism is responsible (removing it degrades performance meaningfully).
- **Failure analysis**: 10–20 qualitative examples where your method fails — this demonstrates scientific honesty and suggests future work.
- **Reproducible artifact**: Any reviewer can `git clone` and `bash run.sh` to reproduce the main table within 30 minutes on a single GPU or CPU.[4](https://www.linkedin.com/pulse/boosting-research-reproducibility-best-practices-data-bir%C3%B3-phd--ykm0f)[3](https://pmc.ncbi.nlm.nih.gov/articles/PMC11828340/)

If you reach the MVR, you have a submittable paper. Every additional experiment beyond this is polish, not necessity. Target arXiv first, then a workshop at a major venue (NeurIPS, ACL, ICLR) to get feedback before a full venue submission.[6](https://theaiinternship.com/blog/ai-research-publication-guide-2025/)[5](https://benjaminnoble.org/blog/minumum-viable-paper)

***

What is the specific domain or problem area you have in mind? (e.g., NLP, computer vision, systems, optimization) — that would allow me to suggest concrete benchmarks, datasets, and baselines tailored to your topic.
