<!-- quality_check: assisted review via same Perplexity stack as sections; not independent empirical validation. See docs/technical/EVALUATION_LAYERS.md -->

This draft outlines a strong extension to arXiv:2510.24256 but lacks executed experiments and reproducibility. Key gaps prevent it from fitting as a standalone arXiv submission targeting replication or novel analysis of that paper.[1](https://arxiv.org/abs/2510.24256)

## Missing Citations
References to arXiv:2510.24256 are over-reliant on HTML versions (e.g., v1/v2) and non-primary sources like moonlight.io reviews or HN threads; cite the canonical PDF/abs directly throughout.[1](https://arxiv.org/abs/2510.24256)
Missing citations for core methods: K-FAC originates from Martens & Grosse (2015), not just target paper; add to baseline table and Phase 1.[1](https://arxiv.org/abs/2510.24256)
Uncited claims like OLMo layer specifics (23-25) or Dolma streaming need sources from OLMo papers (e.g., OLMo et al., 2024).[1](https://arxiv.org/abs/2510.24256)
New proposals (e.g., "curvature index," per-task K-FAC) lack prior art scans; cite related curvature-memorization works like Garg et al. (2024).[1](https://arxiv.org/abs/2510.24256)

## Weak Methodology
No code or hyperparameters for novel elements like activation ratio $$ r_T(p) $$ or fragility correlation; specify computation (e.g., exact percentiles, normalization).[1](https://arxiv.org/abs/2510.24256)
Replication unverified: Draft admits "DEGRADED" status with no K-FAC collection or editing run; methodology copies target paper's setup without confirming on OLMo-2 7B (target uses OLMo-2).[1](https://arxiv.org/abs/2510.24256)
MVRs are aspirational but ungrounded; e.g., per-task K-FAC ignores data efficiency issues (target streams 20M tokens globally).[1](https://arxiv.org/abs/2510.24256)
Editing assumes fixed ρ=0.6 without ablation justification; target paper sweeps layers/projections.[1](https://arxiv.org/abs/2510.24256)

## Unclear Experiments
Results are placeholders (e.g., abstract: "[placeholder; to replace...]"); tables reuse target paper's numbers (e.g., 3.4% strict Dolma) without new runs or error bars.[1](https://arxiv.org/abs/2510.24256)
No figures or actual outputs; e.g., "Figura tipo Fig. 2" references target visuals but shows none here.[1](https://arxiv.org/abs/2510.24256)
Ablations proposed (e.g., ρ=40-80%) but budgets (100 GPU-hours) ignore K-FAC scaling costs on 7B models (~2h/checkpoint per target).[1](https://arxiv.org/abs/2510.24256)
Spectrum extension (e.g., MATH, HotpotQA) undefined: prompts, shots, baselines unclear.[1](https://arxiv.org/abs/2510.24256)

## Ethical/Safety Issues
No discussion of unlearning risks: Edits suppress memorization but degrade math/facts (66-74% retention per target); highlight potential for safety-critical reasoning loss.[1](https://arxiv.org/abs/2510.24256)
Privacy angle underexplored: Target links to verbatim recitation/privacy; draft ignores resurgence post-fine-tuning (noted as gap but unanalyzed).[1](https://arxiv.org/abs/2510.24256)
AI safety claims (e.g., curvature for "cognitive phase transitions") unsubstantiated without results; avoid overhyping unverified interpretability.[1](https://arxiv.org/abs/2510.24256)
No IRB/data ethics for synthetic tasks or Dolma subsets.

## arXiv Formatting Issues
Mixed languages: Title/abstract Spanish, body mixed; arXiv prefers consistent English (target paper is English).[1](https://arxiv.org/abs/2510.24256)
Not LaTeX-ready: Markdown tables, HTML comments (<!-- -->), emojis absent; convert to proper sections (Abstract, 1 Introduction, etc.) with \section{}[2](https://info.arxiv.org/help/faq/mistakes.html)
Excess metadata: Replication banners, disclaimers, timestamps, LLM prompts dilute paper; move to appendix or repo README.[2](https://info.arxiv.org/help/faq/mistakes.html)
No structure: Lacks standard sections (Introduction, Related Work finalized, Results with figures); current is fragmented "sections" like "gaps," "sota."[2](https://info.arxiv.org/help/faq/mistakes.html)
Overlength intros/plans: 8-12 week plan, code lists better as supplements; trim to 8-12 pages core content.[2](https://info.arxiv.org/help/faq/mistakes.html)

What specific MVR (e.g., replication or new tasks) are you prioritizing to execute first?
