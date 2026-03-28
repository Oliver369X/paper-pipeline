<!-- quality_check: assisted review via same Perplexity stack as sections; not independent empirical validation. See docs/technical/EVALUATION_LAYERS.md -->

**This draft outlines a plan to extend BalancedSubnet for memorization mitigation in language models, targeting a technical report venue like arXiv or TMLR.** It draws heavily from the original ICLR 2025 paper but lacks executed novel contributions.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)[2](https://arxiv.org/abs/2410.02159v2)

## Missing Citations
References rely on just 3-5 sources, mostly the core paper and blog; add 10+ for baselines like machine unlearning (e.g., cite Maini et al. 2023 for Greedy, Bourtoule et al. 2021 for general unlearning) and SOTA post-2025 works.[3](https://arxiv.org/html/2410.02159v1)[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Discussion cites speculative arXiv preprints (e.g., 2503.* from 2025); verify/ replace with published papers or recent surveys on LLM unlearning.[3](https://arxiv.org/html/2410.02159v1)
No citations for ethical standards (e.g., NeurIPS/TMLR ethics guidelines) or regional data claims.[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)

## Weak Methodology
"Proposed Method Outline" describes extensions (SAEs for interpretability, adaptive K, Gemma-2B with Bolivian data) without algorithms, pseudocode, or hyperparameters; formalize like original paper's Alg. 6 for BalancedSubnet.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Loss function "LM loss × batch_mask" is vague—specify straight-through estimator details, balancing term equation.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
No theoretical justification for extensions (e.g., why SAEs validate circuits); lacks proofs or bounds on utility-memorization trade-off.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Unclear Experiments
Uses placeholder/example results (e.g., TinyMem-4L: -95% mem diff) without seeds, code, or reproducibility details; TMLR/arXiv demands executable code, raw data.[5](https://arxiv.org/abs/2107.00821)[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)
Baselines lack specifics (e.g., which LoRA-reg? epochs?); ablations undefined (e.g., loss_weight sweep values).[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Pythia results pulled from original paper—no new runs; unclear how to extract Bolivian data or evaluate Gemma.[2](https://arxiv.org/abs/2410.02159v2)

## Ethical/Safety Issues
Disclaimer admits LLM-generated with no executed experiments—unsuitable for research venue claiming results; violates reproducibility ethics.[5](https://arxiv.org/abs/2107.00821)[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)
Discusses "backdoors" but ignores dual-use risks (e.g., pruning for deception removal); no IRB/ethics statement for PII-like data.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
Broader impacts praise safety without addressing limitations like relearning vulnerabilities or adversarial attacks post-pruning.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Formatting Issues
Lowercase "## methodology" (capitalize); inconsistent headers (## experiments vs. ## gaps); no abstract, intro, conclusion—standard arXiv/TMLR expects Title/Abstract/Intro/Methods/Results/Discussion.[6](https://www.sciencepublishinggroup.com/journal/604/preparing-manuscript)[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)
Inline  citations awkward for LaTeX (use \cite); tables need proper Markdown/LaTeX (e.g., no inline citations).[7](https://www.scribd.com/document/646826818/Machine-Learning-Technical-Report)[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)
LLM comments, timestamps, Spanish disclaimer informal; remove for polish. Use TMLR LaTeX template (PDF, any length justified).[4](https://jmlr.csail.mit.edu/tmlr/author-guide.html)
