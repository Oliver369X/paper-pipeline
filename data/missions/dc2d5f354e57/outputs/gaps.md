<!-- section=gaps generated=2026-03-27T16:30:07.918499+00:00 model=best -->

BalancedSubnet effectively mitigates memorization in language models by pruning subnetworks responsible for memorized sequences while balancing general task performance, but several gaps remain underexplored.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Key Gaps

- **Scaling to massive models (>10B params):** Tested only up to Pythia-6.9B; lacks evaluation on frontier LLMs where subnet localization may degrade due to parameter scale.[2](https://arxiv.org/abs/2410.02159v2)
- **Long-context memorization:** Focuses on short synthetic sequences; untested on real-world long-context regurgitation in extended prompting regimes.
- **Adversarial extraction attacks:** No assessment against advanced membership inference or extraction attacks post-unlearning, risking residual leakage.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
- **Multi-modal models:** Limited to text-only GPT-2-style architectures; applicability to vision-language or audio models undemonstrated.
- **Mechanistic interpretability:** Pruning lacks causal analysis of excised circuits; unclear if it targets true memorization mechanisms vs. proxies.[3](https://mansisak.com/memorization/)
- **Efficiency in continual unlearning:** Single-shot only; no streaming or repeated unlearning for dynamic forget sets, critical for production.
- **Real memorized data diversity:** Relies on synthetic noise/backdoors; gaps in copyrighted, PII, or multilingual real extracts from Pile/C4.[2](https://arxiv.org/abs/2410.02159v2)
- **Theoretical guarantees:** Empirical balancing term unproven; lacks bounds on utility-memorization trade-off or approximation error.[1](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)
