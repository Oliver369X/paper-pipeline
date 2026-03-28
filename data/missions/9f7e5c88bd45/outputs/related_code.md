<!-- section=related_code generated=2026-03-27T18:08:51.585920+00:00 model=best -->

No direct open-source repositories implement "Curvatura de Pérdida K-FAC" specifically for memorization mitigation in Small Language Models (SLMs), as this appears to reference recent research on K-FAC (Kronecker-Factored Approximate Curvature) for loss curvature analysis in larger LMs like OLMo-2. Related implementations focus on K-FAC for curvature-memorization links or general optimization, adaptable to SLMs with modifications.[1](https://arxiv.org/html/2510.24256v2)[2](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature)[3](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)[4](https://arxiv.org/html/2510.24256v1)

## K-FAC Memorization Repos

| Repository | URL | License | Last Update | Relevance |
|------------|-----|---------|-------------|-----------|
| omrifahn/kfac-memorization-code | https://huggingface.co/datasets/omrifahn/kfac-memorization-code | MIT | Recent (2025 activity via downloads)  | Implements K-FAC weight editing to prune low-curvature components suppressing memorization in LMs like OLMo; includes collectors, editors, and evaluation for next-token prediction. [3](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)[1](https://arxiv.org/html/2510.24256v2) |
| DeepakTatachar/Privacy-Memorization-Curvature | https://github.com/DeepakTatachar/Privacy-Memorization-Curvature | MIT | Jun 2024 [1](https://arxiv.org/html/2510.24256v2) | Official ICML 2024 code linking input loss curvature to memorization/privacy; computes curvature scores on vision models (CIFAR/ImageNet), extensible to SLM loss landscapes. [2](https://github.com/DeepakTatachar/Privacy-Memorization-Curvature) |
| purdue-nrl/Memorization-Curvature | https://github.com/purdue-nrl/Memorization-Curvature | Not specified in results | ICML 2024 Spotlight [5](https://github.com/purdue-nrl/Memorization-Curvature) | Analyzes memorization via per-sample loss curvature (not K-FAC); provides baseline for curvature-based mitigation experiments. [5](https://github.com/purdue-nrl/Memorization-Curvature) |

## General K-FAC Libraries

These provide core K-FAC approximations for custom curvature loss implementations in SLMs.

- **tensorflow/kfac**: https://github.com/tensorflow/kfac – Apache 2.0; last major 2018; K-FAC optimizer for TensorFlow, foundational for Hessian/curvature approx.[6](https://github.com/tensorflow/kfac)
- **google-deepmind/kfac-jax**: https://github.com/google-deepmind/kfac-jax – Apache 2.0; 2022; JAX library for scalable curvature and second-order optimization in NNs.[7](https://github.com/google-deepmind/kfac-jax)

For SLM-specific adaptation, start with omrifahn's code on small models like SmolLM-135M and integrate K-FAC pruning.[8](https://huggingface.co/HuggingFaceTB/SmolLM-135M)[3](https://huggingface.co/datasets/omrifahn/kfac-memorization-code)
