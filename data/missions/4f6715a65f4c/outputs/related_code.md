<!-- section=related_code generated=2026-03-29T06:14:36.852543+00:00 model=best -->

Below are open‑source repositories, libraries, and reference implementations directly or closely related to *“From Memorization to Reasoning in the Spectrum of Loss Curvature”* (arXiv:2510.24256). Each entry includes URL, license (where visible), last‑update signal, and a one‑line relevance.

***

- **Goodfire AI official K‑FAC + memorization‑editing code**  
  URL: https://github.com/goodfire-ai/memorization_kfac  
  License: Not explicitly stated in repo front page; paper/blog do not specify; likely **research‑oriented open license** (commonly MIT / Apache‑style for this group).  
  Last update: First commit / tags around late 2025, with activity aligned with the October 2025 paper release.  
  Relevance: **Direct reference implementation** of the K‑FAC‑based curvature estimation and low‑curvature‑subspace editing for LLMs/ViTs described in arXiv:2510.24256.  

- **Goodfire AI blog / research page (method description + context)**  
  URL: https://www.goodfire.ai/research/understanding-memorization-via-loss-curvature  
  License: Website content; code links are to the above repo.  
  Last update: Posts dated November 5–6, 2025, with the K‑FAC‑editing explanation and high‑level code sketch.  
  Relevance: **Annotated walkthrough of the four‑step K‑FAC‑editing pipeline**, useful for understanding how to plug the method into arbitrary LMs.  

- **K‑FAC‑JAX (official K‑FAC library for JAX models)**  
  URL: https://github.com/google/kfac  
  License: Apache‑2.0 (standard Google ML library).  
  Last update: Active repo; recent commits and releases in 2024–2025.  
  Relevance: **High‑quality K‑FAC backend** you can reuse or adapt to compute activation‑gradient covariances $$G \otimes A$$ for your own curvature‑based editing experiments.[1](https://kfac-jax.readthedocs.io/en/latest/advanced.html)[2](https://github.com/tensorflow/kfac/blob/master/docs/index.md)

- **TensorFlow K‑FAC implementation (for TF models)**  
  URL: https://github.com/tensorflow/kfac  
  License: Apache‑2.0.  
  Last update: Code last touched in 2018–2019; docs indicate legacy but still usable implementation.  
  Relevance: **Reference K‑FAC implementation** if you want to reimplement curvature estimation in TensorFlow or inspect the classical K‑FAC factorization pattern.[2](https://github.com/tensorflow/kfac/blob/master/docs/index.md)

- **arXiv‑hosted paper page (with discussion / potential community forks)**  
  URL: https://arxiv.org/abs/2510.24256 (also https://huggingface.co/papers/2510.24256)  
  License: Paper is under arXiv non‑exclusive license, code links refer to the above GitHub repo.  
  Last update: Paper version v2 dated October 31, 2025.  
  Relevance: **Canonical artifact for citation** and **entry point to any community‑forked adaptations** of the method (e.g., Hugging Face discussions, Reddit threads, etc.).[3](https://huggingface.co/papers/2510.24256)[4](https://arxiv.org/abs/2510.24256)

- **Reddit / social‑thread discussions (community‑driven pointers)**  
  URL (example): https://www.reddit.com/r/ArtificialInteligence/comments/1ov65jx/from_memorization_to_reasoning_in_the_spectrum_of/  
  License: Forum content; no explicit license.  
  Last update: Posts around November 2025, discussing the experiments and asking for code links.  
  Relevance: **Community‑driven overview and pointer to implementation details** such as dataset choices and practical gotchas in K‑FAC passes.[5](https://www.techzeitgeist.de/memorization-vs-reasoning-neural%E2%80%91pfade-in-llms-verstehen/)[6](https://www.reddit.com/r/ArtificialInteligence/comments/1ov65jx/from_memorization_to_reasoning_in_the_spectrum_of/)

***

If you want, I can next sketch a **minimal fork‑and‑run recipe** (e.g., “how to clone `goodfire-ai/memorization_kfac` and run it on a 2–3B LM on a single A100”) tailored to your hardware.
