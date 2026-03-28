<!-- section=gaps generated=2026-03-24T02:22:16.117406+00:00 model=claude-sonnet-4.6-thinking -->

Here are the key open problems, methodological gaps, and underexplored settings in the **Research and Build** space that are well-suited for a GitHub-targeted submission:

## Reproducibility & Replication

- **No standardized "build-ready" artifact format for research papers** — most papers ship code as an afterthought with no CI/CD, making exact replication nearly impossible without heroic effort[1](https://arxiv.org/abs/2503.04921)
- **Absence of versioned research-to-code mapping** — when a paper is revised, there is no automated mechanism linking the updated claim to the corresponding code change in the repo[2](https://arxiv.org/html/2509.03565v1)
- **Underexplored: multi-paper method chains** — tracking how methodology evolves across a sequence of related works (e.g., paper A → paper B → paper C) is structurally unsupported by existing tooling[2](https://arxiv.org/html/2509.03565v1)

## Research-to-Production Transition

- **The research↔production chasm remains unmeasured** — only ~13% of AI/ML projects survive from notebook to production, yet no open benchmark captures *where* and *why* pipelines fail at each handoff stage[3](https://www.linkedin.com/pulse/bridging-gap-between-aiml-experimentation-production-butkevi%C4%8Dius)
- **Build pipelines lack intelligent test selection** — only 17% of organizations select test cases based on applicable code changes, meaning research codebases carry enormous redundant CI overhead[4](https://www.harness.io/the-state-of-software-engineering-excellence)[5](https://www.morningstar.com/news/pr-newswire/20250617sf11937/new-report-reveals-alarming-state-of-software-engineering-excellence-most-organizations-failing-to-deliver-on-developer-experience-and-devops-maturity)
- **Schema drift and data distribution shift are under-tooled** — production systems face noisy, late, and malformed data, but research repos rarely ship monitoring or alerting primitives alongside model code[6](https://www.linkedin.com/posts/utkarshwadhwa_aiengineering-mlops-productionai-activity-7358323398395006977-oMq2)

## Open-Source Collaboration Gaps (GitHub-Specific)

- **Feature request lifecycle is inconsistently labeled** — a large-scale study of 1.4M GitHub issues found labeling practices are often incoherent across projects, blocking automated triage and prioritization research[7](https://conf.researchr.org/details/ase-2025/ase-2025-papers/236/Understanding-Feature-Request-Practice-on-GitHub-via-a-Large-Scale-Empirical-Study)
- **Experienced-contributor bias in issue resolution** — feature requests from experienced contributors are disproportionately resolved, creating a structural barrier for newcomer-driven research extensions[7](https://conf.researchr.org/details/ase-2025/ase-2025-papers/236/Understanding-Feature-Request-Practice-on-GitHub-via-a-Large-Scale-Empirical-Study)
- **No formalized acceptance criteria for research issues** — over 25% of engineering leaders report >70% of requirements lack clearly defined acceptance criteria, a gap especially acute in research repos where scope creep exceeds 20% per sprint[5](https://www.morningstar.com/news/pr-newswire/20250617sf11937/new-report-reveals-alarming-state-of-software-engineering-excellence-most-organizations-failing-to-deliver-on-developer-experience-and-devops-maturity)

## Build Infrastructure

- **64% of infrastructure deployments are still manual** — research repos targeting reproducibility have no standard toolchain for infrastructure-as-code, making environment setup a dominant hidden cost[5](https://www.morningstar.com/news/pr-newswire/20250617sf11937/new-report-reveals-alarming-state-of-software-engineering-excellence-most-organizations-failing-to-deliver-on-developer-experience-and-devops-maturity)
- **CI pipeline complexity is understudied qualitatively** — existing work measures build time but rarely employs surveys or interviews to capture *why* teams make specific pipeline design trade-offs[8](https://cse3000-research-project.github.io/static/6f7c182b88c2d1ab61330d91c3236834/poster.pdf)
- **FAIR principles adoption in research software is sparse** — tools like PyPackIT exist but are not widely adopted; most research GitHub repos violate Findable/Interoperable/Reusable criteria by default[1](https://arxiv.org/abs/2503.04921)

## Methodological Blind Spots

- **Isolated method comparisons dominate; pipeline-oriented evaluation is rare** — most benchmarks compare individual methods, not cumulative pipelines, hiding compounding errors across stages[9](https://www.sciencedirect.com/science/article/pii/S0957417426002794)
- **Research gap identification itself is manual and non-scalable** — no robust automated tool exists to map the space of "what is known" vs. "what is needed" across a live GitHub topic cluster[10](https://lennartnacke.com/the-7-research-gaps/)[11](https://towardsai.net/p/machine-learning/how-to-identify-ai-ml-research-problems-worth-solving)
- **Underexplored setting: low-resource / low-staffing research teams** — nearly all build tooling assumes well-resourced teams; small labs in developing contexts (e.g., limited cloud budget, intermittent CI) have no tailored methodology[1](https://arxiv.org/abs/2503.04921)
