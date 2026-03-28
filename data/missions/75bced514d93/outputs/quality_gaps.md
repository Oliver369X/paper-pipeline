<!-- quality_check -->

This draft has significant structural, methodological, and scholarly issues across every dimension. Here is a complete gap analysis organized by category.

***

## Missing or Weak Citations

- **Vendor/press-release sources standing in for peer-reviewed evidence.** The "~13% AI/ML projects survive notebook-to-production" claim cites a LinkedIn Pulse article; the "17% of organizations select tests based on code changes" and "64% of deployments are still manual" statistics both cite a Harness.io vendor report and a PR Newswire press release. None of these are acceptable primary citations for a research venue.[1](https://reviewerone.com/blog/how-to-assess-methodology-as-a-peer-reviewer/)
- **Uncited quantitative claims.** The assertion that "scope creep exceeds 20% per sprint" in research repos has zero citation anywhere in the draft, yet it is stated as fact.
- **Blog posts and personal sites used as methodology sources.** The "Minimal Viable Result" framework and the four-step pipeline are cited to personal blogs (benjaminnoble.org, aryanrahman.dev, userinterviews.com) rather than peer-reviewed methodology papers.[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8965503/)
- **Undefined acronyms in citations.** The metrics table lists "Train–Val gap (LOR / COS)" — LOR and COS are never defined anywhere in the draft, and no citation is provided to explain them.
- **BLEU/ROUGE listed without caveats.** The draft recommends BLEU and ROUGE as generation metrics without citing or acknowledging their well-documented limitations (e.g., BERTScore, chrF, or BLEURT as modern alternatives).

***

## Weak Methodology

- **No actual research contribution exists.** The entire draft describes *how to write a paper*, not what *this paper's* contribution is. There is no hypothesis, no problem statement, and no original claim. This would be an immediate desk reject at any venue.
- **Insufficient statistical rigor.** Recommending "3 random seeds" as sufficient for statistical validity is below current field standards; most venues expect 5–10 seeds with confidence intervals or formal hypothesis tests (e.g., paired t-test, bootstrap CIs).[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8965503/)
- **Baseline fairness is unaddressed.** There is no discussion of how hyperparameters are tuned for baselines vs. the proposed method — a standard source of unfair comparison that reviewers flag routinely.[1](https://reviewerone.com/blog/how-to-assess-methodology-as-a-peer-reviewer/)
- **"30 minutes on a single GPU or CPU" is unspecified.** No hardware tier, VRAM, or CPU spec is given — making this reproducibility claim unverifiable.
- **No negative results protocol.** The methodology has no guidance for what to do if the proposed method does not beat baselines, which creates a publication-bias blind spot.

***

## Unclear Experiments

- **All results are placeholder values.** The entire Results Table is filled with "xx.x ± x.x" — no actual experiment has been run or described.
- **No dataset is specified.** Train/val/test splits are mentioned in passing but no concrete dataset, size, class balance, or provenance is given.
- **No significance testing protocol.** The experiments section never mentions when a difference is statistically significant (p-value threshold, effect size, or correction for multiple comparisons).
- **Cross-validation strategy is absent.** No mention of k-fold CV, stratified splits, or temporal splits for time-series data.
- **Scaling curve methodology is undefined.** "Vary model size or training data volume" is mentioned without specifying axes, ranges, or what conclusions would be valid from such a curve.
- **Computational budget percentages are asserted, not justified.** The allocation (e.g., "~40% for ablations") is presented as a rule with a single ICML citation, but no justification is given for why these ratios apply to the described setting.

***

## Ethical & Safety Issues

- **No data ethics or licensing section.** The draft references scraping 1.4 million GitHub issues with no discussion of ToS compliance, user privacy, or IRB-equivalent review for large-scale data collection.
- **No environmental/compute impact statement.** Reporting CO₂ equivalent or compute hours is now standard or required at NeurIPS, ICLR, and ACL venues; it is entirely absent here.[2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8965503/)
- **No fairness or bias analysis.** The draft mentions calibration metrics (ECE, Brier Score) for "safety-critical applications" but includes no fairness metrics (demographic parity, equalized odds) or discussion of disparate impact.
- **No broader impact or dual-use statement.** For AI/ML work, most venues require a broader impact section discussing potential misuse; the draft has none.
- **No LICENSE file prescribed.** The GitHub artifact checklist (README, Dockerfile, scripts) omits a LICENSE file entirely — without one, the repo is legally "all rights reserved" by default, which directly contradicts the open reproducibility goals of the paper.

***

## Formatting Issues (GitHub + Generic Venue)

| Issue | Location | Impact |
|---|---|---|
| **No Abstract** | Entire draft | Immediate reject at any venue |
| **No Introduction or Related Work sections** | Entire draft | Core paper structure missing |
| **No Conclusion** | Entire draft | Required for every venue |
| **Title is "Research y build"** (`y` = "and" in Spanish) | Title block | Localization bug; non-English title fragment |
| **HTML comment metadata visible** (`<!-- section=gaps generated=... model=... -->`) | All sections | Template artifact leaking into manuscript |
| **Internal generation timestamp in body** | Header | Should be removed before submission |
| **Inline URL citations** (e.g., `[1](https://reviewerone.com/blog/how-to-assess-methodology-as-a-peer-reviewer/)(https://arxiv.org/...)`) | All sections | No `.bib` file; incompatible with LaTeX/arXiv/any venue style |
| **Inconsistent heading numbering** | experiments vs. other sections use `## 1.` vs. unnumbered `##` | Style inconsistency |
| **Unanswered clarifying questions at end of sections** | methodology, experiments | Placeholder prompts must be removed |
| **No `CONTRIBUTING.md` or `CODE_OF_CONDUCT.md`** | GitHub repo spec | Expected for open-source research repos [3](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories) |
| **No issue/PR templates defined** | GitHub repo spec | Inconsistent with the paper's own claim about GitHub issue labeling gaps |

The most critical single issue is that **the draft contains no original research contribution** — it is a meta-guide for writing a paper, not a paper itself. Every other gap is secondary until a concrete hypothesis, dataset, method, and results are defined.
