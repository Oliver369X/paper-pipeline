<!-- section=sota generated=2026-03-27T16:30:21.708851+00:00 model=best -->

**BalancedSubnet represents the current state-of-the-art method for mitigating memorization in language models through machine unlearning.**[1](https://arxiv.org/abs/2410.02159v2)

Introduced in the ICLR 2025 paper "Mitigating Memorization in Language Models," it extends the Subnet approach by training a binary mask to identify and prune subnetworks responsible for memorized sequences while penalizing masks that affect non-memorized tasks.  This weight-based unlearning technique outperforms regularizers, fine-tuning, and other unlearning methods (e.g., Greedy, Durable, neuron-based like Hard Concrete) in reducing regurgitation while preserving downstream performance and efficiency.[2](https://www.stat.berkeley.edu/~mmahoney/pubs/12369_Mitigating_Memorization_.pdf)

## Benchmarks
TinyMem suite serves as the primary benchmark, including small GPT-2-style models for rapid testing. 
- Math sequence models (additive/multiplicative synthetic sequences with noise/backdoor artifacts). 
- Toy language models (Wikipedia corpus with noise/backdoor artifacts). 
Production validation uses Pythia models (2.8B and 6.9B parameters, trained on The Pile).[1](https://arxiv.org/abs/2410.02159v2)

## Metrics
Standard metrics evaluate three key aspects. 

| Metric | Description | Goal |
|--------|-------------|------|
| % Memorized | % of artifact sequences (noise/backdoors) regurgitated verbatim via greedy decoding | Lower (ideally ~0%)  |
| Accuracy (math) / Perplexity (language) | Test performance on clean tasks post-mitigation | Higher accuracy / Lower perplexity (close to baseline)  |
| Time (seconds) | Computation time for mitigation | Lower  |

## Performance
BalancedSubnet achieves near-complete memorization removal (0-0.06% memorized) with minimal degradation (e.g., 96.11-96.79% accuracy on math, perplexity 57.18-71.86 on language for 4-layer TinyMem). 

| Model | Artifact | % Memorized (Baseline → BalancedSubnet) | Accuracy/Perplexity (Baseline → BalancedSubnet) | Time (sec)  |
|-------|----------|-----------------------------------------|-------------------------------------------------|--------------------|
| TinyMem Math 4L | Noise | 34.73 → 0.06 | 96.98 → 96.11% | 6.00 |
| TinyMem Math 4L | Backdoor | 99.50 → 0.00 | 96.97 → 96.79% | 5.88 |
| TinyMem Lang 4L | Noise | 13.06 → 0.00 | 56.87 → 57.18 | 92.56 |
| TinyMem Lang 4L | Backdoor | 100.00 → 0.00 | 63.15 → 71.86 | 917.96 |
| Pythia 2.8B | Memorized seqs | 53.47 → 9.11 | 21.98 → 23.02 | 88.97 |
| Pythia 6.9B | Memorized seqs (ASR) | 89.31 → 6.53 | 19.46 → 22.73 | 233.42 |

It consistently excels across model sizes (2-16 layers), training durations, and data sizes, often reducing % memorized by ~100% with <5% performance drop. 

## Architectures
Applies to GPT-2-style autoregressive transformers, from tiny models (e.g., 4 layers) to production-scale like Pythia (up to 6.9B params).  Code and TinyMem available at https://github.com/msakarvadia/memorization.[3](https://github.com/msakarvadia/memorization)
