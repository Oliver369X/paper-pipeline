<!-- section=related_code generated=2026-03-27T16:43:42.091569+00:00 model=best -->

Here are open‑source repositories and codebases directly or closely related to **BalancedSubnet** for mitigating memorization in language models, with license, freshness, and one‑line relevance:

***

### 1. Original “Mitigating Memorization in Language Models” codebase  
- **URL**: https://github.com/msakarvadia/memorization[1](https://github.com/msakarvadia/memorization)[2](https://github.com/msakarvadia/memorization/blob/main/README.md)
- **License**: MIT[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Repository created in 2024; last commit logs and issue activity indicate active development through at least early 2025.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Reference implementation of **BalancedSubnet** and other unlearning‑based memorization‑mitigation methods; includes TinyMem models and scripts for applying BalancedSubnet to both toy and Pythia‑scale LMs.[3](https://arxiv.org/abs/2410.02159v2)[4](https://arxiv.org/html/2410.02159v1)[1](https://github.com/msakarvadia/memorization)

***

### 2. TinyMem / unlearning experiments (same repo)  
- **URL**: `memorization/localize/weight/` and `localize_memorization.py` / `prod_grad.py` in the same repo[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **License**: MIT (same as above)[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Subdirectory code and scripts updated in line with the main repo; last‑run CSVs and notebooks indicate experiments through 2025.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Contains the core **BalancedSubnet weight‑level unlearning** implementation (learnable binary mask + dual‑objective loss) and Pythia‑compatible unlearning scripts, making it the closest reference‑implementation for your own BalancedSubnet experiments.[4](https://arxiv.org/html/2410.02159v1)[3](https://arxiv.org/abs/2410.02159v2)[1](https://github.com/msakarvadia/memorization)

***

### 3. TinyMem / loss‑landscape visualization notebooks  
- **URL**: `memorization/vis/` and ` Visualization_Notebook.ipynb` / `pythia_unlearning_results.ipynb` in the same repo[1](https://github.com/msakarvadia/memorization)[2](https://github.com/msakarvadia/memorization/blob/main/README.md)
- **License**: MIT[1](https://github.com/msakarvadia/memorization)
- **Last‑update signal**: Jupyter notebooks and CSVs were last updated in 2025, with full Pythia unlearning runs and “best runs” CSVs.[2](https://github.com/msakarvadia/memorization/blob/main/README.md)[1](https://github.com/msakarvadia/memorization)
- **Relevance**: Provides a ready setup for **visualizing BalancedSubnet edits** (e.g., loss landscapes before/after) and reproducing the paper’s Pythia 2.8B/6.9B experiments.[3](https://arxiv.org/abs/2410.02159v2)[4](https://arxiv.org/html/2410.02159v1)[1](https://github.com/msakarvadia/memorization)

***

### 4. Goodfire AI memorization / unlearning research (reference use of BalancedSubnet)  
- **URL**: https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **License**: Not a full BalancedSubnet codebase; likely refers to internal or separate code, but explicitly cites BalancedSubnet as a baseline.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **Last‑update signal**: Published blog/research note in late 2025.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)
- **Relevance**: Conceptual reference that **uses BalancedSubnet (BSN)** as an SOTA unlearning baseline for evaluating memorization via loss‑curvature, useful if you want to compare or extend BalancedSubnet‑style masking.[5](https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature)

***

If you tell me whether you want a **concrete replication script for BalancedSubnet on TinyMem** or instead on a Pythia‑scale model (e.g., Pythia‑2.8B/6.9B), I can summarize the minimal file set and config to drop into your own repo.
