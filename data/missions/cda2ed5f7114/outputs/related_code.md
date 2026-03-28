<!-- section=related_code generated=2026-03-27T20:38:27.294024+00:00 model=best -->

Here is a curated list of open‑source repositories and core libraries relevant to *análisis de la curvatura de pérdida en la transición memorización–razonamiento*. For each I give URL, license (if visible), last‑update signal, and one‑liner on relevance.

***

### 1. **From Memorization to Reasoning in the Spectrum of Loss Curvature (author‑linked code)**

- **URL:** https://github.com/DeepakTatachar/Privacy-Memorization-Curvature[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **License:** Typically per‑paper licenses (often BSD‑style or MIT‑like; check repo `LICENSE` / `README` directly).[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **Last‑update signal:** Repository tagged as “code for Unveiling Privacy, Memorization and Input Loss Curvature” (2024‑style project).[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)
- **Relevance:** Provides an official implementation for analyzing memorization and privacy via input‑wise loss‑curvature; useful as a reference for how curvature per‑sample can be used to flag memorized or high‑risk examples.[1](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)

***

### 2. **K‑FAC curvature estimators (K‑FAC‑JAX / JAX‑level)**

- **URL (K‑FAC‑JAX):** https://github.com/google-deepmind/kfac-jax[2](https://github.com/google-deepmind/kfac-jax)
- **License:** Apache 2.0 (clearly stated in repo).[2](https://github.com/google-deepmind/kfac-jax)
- **Last‑update signal:** Commit history and quickstart docs show active maintenance into 2022–2024 band.[2](https://github.com/google-deepmind/kfac-jax)
- **Relevance:** Lightweight, scalable K‑FAC library for computing Hessian‑type curvature approximations in JAX; directly usable for loss‑curvature analysis (e.g., the “From Memorization to Reasoning…” style decompositions at the MLP / transformer layer).[3](https://arxiv.org/html/2510.24256v1)[2](https://github.com/google-deepmind/kfac-jax)

***

### 3. **K‑FAC in TensorFlow (TF reference)**

- **URL:** https://github.com/tensorflow/kfac[4](https://github.com/tensorflow/kfac)
- **License:** Apache 2.0 (explicit in repo).[4](https://github.com/tensorflow/kfac)
- **Last‑update signal:** Commits and releases span 2018–2020; less actively updated but still functional.[4](https://github.com/tensorflow/kfac)
- **Relevance:** Canonical TensorFlow implementation of K‑FAC, useful if you want to plug curvature‑based memorization analysis into legacy TF‑based vision or language models.[3](https://arxiv.org/html/2510.24256v1)[4](https://github.com/tensorflow/kfac)

***

### 4. **Memorization‑via‑curvature (per‑sample curvature) reference**

- **URL (paper):** https://arxiv.org/abs/2307.05831[5](https://arxiv.org/abs/2307.05831)
- **License:** Paper is CC‑BY or similar (standard arXiv); any code repo is not explicitly linked here, but the authors describe per‑sample curvature estimation around training points.[5](https://arxiv.org/abs/2307.05831)
- **Last‑update signal:** Preprint v2 updated 2 Oct 2023.[5](https://arxiv.org/abs/2307.05831)
- **Relevance:** Conceptual/algorithmic foundation for using local curvature of the loss function around individual samples as a memorization proxy; you can implement this on top of K‑FAC or similar Hessian‑approximation stacks.[3](https://arxiv.org/html/2510.24256v1)[5](https://arxiv.org/abs/2307.05831)

***

### 5. **K‑FAC “classic” implementation (PyTorch‑style)**

- **URL:** https://github.com/Xin-Jing/K-FAC[6](https://github.com/Xin-Jing/K-FAC)
- **License:** Repo does not spell out license prominently, but the codebase is small and oriented toward research reuse.[6](https://github.com/Xin-Jing/K-FAC)
- **Last‑update signal:** Initial commits in 2017; last sizable pushes around 2018–2019.[6](https://github.com/Xin-Jing/K-FAC)
- **Relevance:** Simple, pedagogical K‑FAC implementation; handy if you want a minimal codebase to adapt for loss‑curvature experiments on memorization–reasoning in small MLPs or conv‑nets.[3](https://arxiv.org/html/2510.24256v1)[6](https://github.com/Xin-Jing/K-FAC)

***

### 6. **General “loss‑landscape / curvature / deep‑phenomena” curation**

- **URL (awesome‑deep‑phenomena):** https://github.com/MinghuiChen43/awesome-deep-phenomena[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **License:** N/A (collection of links and papers).[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **Last‑update signal:** Last commits in 2020–2021; still useful as a curated index.[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)
- **Relevance:** Collects many empirical studies on loss‑landscape flatness, curvature, and memorization; can guide you to additional papers with associated codebases for curvature‑based analysis.[7](https://github.com/MinghuiChen43/awesome-deep-phenomena)

***

If you tell me whether you want to work in **PyTorch** vs **JAX** and whether you’re targeting **per‑sample curvature** or **parameter‑space curvature (K‑FAC‑style)**, I can compose a minimal end‑to‑end example script (e.g., “compute loss‑curvature per‑sample for a small MLP and then threshold by curvature to probe memorization”).
