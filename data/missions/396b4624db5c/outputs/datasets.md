<!-- section=datasets generated=2026-03-26T21:00:17.184581+00:00 model=best -->

Public datasets for Sparse Autoencoders (SAEs) in mechanistic interpretability primarily consist of model activation dumps or benchmark suites derived from open LLMs like Pythia and Gemma, trained on corpora such as The Pile. These enable SAE training/evaluation without recomputing activations.[1](https://huggingface.co/papers?q=Sparse+autoencoders)[2](https://github.com/jbloomAus/SAELens)

## Activation Datasets

| Name | Access URL | License | Approx. Size | Modalities | Caveats |
|------|------------|---------|--------------|------------|---------|
| Pythia Activations (via SAELens) | https://huggingface.co/datasets/jbloom/GPT2-Small-SAEs-Pythia-Activations | MIT | 160M-2.8B tokens/layer (e.g., 500M+ for training) | Text residuals (embeddings/MLPs) | Pile skew (web-heavy, English-centric); potential label noise from tokenizer quirks; no recent temporal drift as static.[2](https://github.com/jbloomAus/SAELens) |
| Gemma-2 Activations (Gemma-Scope/SAEBench) | https://huggingface.co/datasets/gemma-scope/Gemma-2-2B-activations_layer_12; https://huggingface.co/NousResearch/SAEBench | Apache 2.0 | 100M-1B tokens/layer (e.g., 65k SAE widths) | Text residuals (layer 12 focus) | Web/fine-tune bias (chat variants); geography: English-dominant; minor drift if post-2024 Pile subsets.[3](https://www.neuronpedia.org/sae-bench/info) |
| GPT2-Small Activations | https://huggingface.co/datasets/NeelNanda/GPT2-small-activations | MIT | ~8B tokens (TransformerLens format) | Text residuals/MLPs | OpenWebText (pre-2020, outdated facts); high noise in factual recall; US-English heavy.[4](https://transformer-circuits.pub/2023/monosemantic-features)[5](https://www.perplexity.ai/search/ca3e1039-a249-44be-925b-62d93d64cdc4) |

## Benchmark Datasets

| Name | Access URL | License | Approx. Size | Modalities | Caveats |
|------|------------|---------|--------------|------------|---------|
| SAEBench | https://www.neuronpedia.org/sae-bench; https://huggingface.co/NousResearch/SAEBench | MIT | 200+ SAEs + evals (e.g., 4k-65k widths) | Text tasks (sparse probing, unlearning) | Derived from Pythia/Gemma; label noise in bios/reviews; temporal drift in news (AG News pre-2010).[3](https://www.neuronpedia.org/sae-bench/info) |
| Neuronpedia SAE Hub | https://www.neuronpedia.org | Apache 2.0 | Millions activations + SAEs | Text residuals/features | Aggregated (various sources); inconsistent geography (mostly English/Western); noise from diverse tokenizers.[3](https://www.neuronpedia.org/sae-bench/info)
