<!-- section=datasets generated=2026-03-27T18:08:32.170697+00:00 model=best -->

## Relevant Datasets

Public datasets directly tied to K-FAC curvature loss for memorization mitigation in SLMs are scarce, as this is a specialized recent technique often tested on standard small-scale corpora. Key examples used in related memorization studies for small models include UCI/OpenML tabular sets and text benchmarks like Pile subsets.[1](https://github.com/interpretml/LLM-Tabular-Memorization-Checker)[2](https://arxiv.org/html/2507.06056v1)[3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html)

## Tabular Datasets (via tabmemcheck)

These UCI/OpenML datasets are perturbed for memorization testing in SLMs/LLMs, ideal for evaluating curvature-based overfitting due to their small size and structured nature.[3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html)[1](https://github.com/interpretml/LLM-Tabular-Memorization-Checker)

| Name | Access URL | License | Approx. Size | Modalities | Caveats |
|------|------------|---------|--------------|------------|---------|
| OpenML Diabetes | https://www.openml.org/d/40675 | Public Domain (OpenML) | 101k rows, 20 cols (~10MB CSV) | Tabular (numerical/clinical) | US geography bias; potential label noise in medical self-reports [1](https://github.com/interpretml/LLM-Tabular-Memorization-Checker) |
| Adult (Census Income) | https://archive.ics.uci.edu/dataset/2/adult | UCI public | 48k rows, 14 cols (~5MB) | Tabular (demographic) | US-centric (1990s data), temporal drift; class imbalance [3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html) |
| Iris | https://archive.ics.uci.edu/dataset/53/iris | UCI public | 150 rows, 5 cols (<1MB) | Tabular (botanical) | Minimal noise; very small, risks overfitting in any SLM [3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html) |
| UCI Wine | https://archive.ics.uci.edu/dataset/109/wine | UCI public | 178 rows, 14 cols (<1MB) | Tabular (chemical) | Italy geography; low noise but tiny size [3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html) |
| California Housing | https://www.openml.org/d/4134 | OpenML | 20k rows, 9 cols (~2MB) | Tabular (real estate) | California-only (US geography bias); 1990s temporal drift [3](http://interpret.ml/LLM-Tabular-Memorization-Checker/api_reference.html) |

## Text Benchmarks for SLMs

These are used in SLM memorization papers, suitable for K-FAC experiments on duplication/overfitting in language tasks.[2](https://arxiv.org/html/2507.06056v1)[4](https://github.com/EleutherAI/pile-cc)[5](https://github.com/livebench/livebench)

| Name | Access URL | License | Approx. Size | Modalities | Caveats |
|------|------------|---------|--------------|------------|---------|
| LiveBench | https://github.com/livebench/livebench | MIT | ~25k questions (monthly updates, ~50MB JSONL) | Text (QA/math/coding) | Low contamination by design; recent data reduces temporal drift but English-heavy [5](https://github.com/livebench/livebench) |
| Pile-CC (MIMIR subset) | https://github.com/EleutherAI/pile-cc | Apache 2.0 | Full: ~200TB; subsets ~GBs | Text (web/common crawl) | Web scrapes (global but English-dominant); duplication/noise common [4](https://github.com/EleutherAI/pile-cc)[2](https://arxiv.org/html/2507.06056v1) |

For K-FAC specifically (as in arXiv:2510.24256), authors use custom transformer setups on toy duplicates of these or C4-like subsets, but no dedicated public release found. What SLM architecture or base dataset are you targeting for experiments?[6](https://www.youtube.com/watch?v=5kWG5Hpi-Uo)
