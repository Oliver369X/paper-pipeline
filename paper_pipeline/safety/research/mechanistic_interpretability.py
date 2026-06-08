"""Mechanistic Interpretability Research Framework.

This module implements interpretability techniques from:
- "Towards Monosemanticity" (Anthropic, 2023)
- "Sparse Autoencoders" (Cunningham et al., 2023)
- "Transformer Circuits" (Elhage et al., 2021)

For analyzing small language models (1B-7B) using:
- TransformerLens for activation extraction
- Sparse Autoencoders for feature decomposition
- Attention pattern analysis
- Probing classifiers

Requirements:
- torch
- transformer_lens
- sae-lens (for sparse autoencoders)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InterpretabilityConfig:
    """Configuration for interpretability analysis."""

    # Model
    model_name: str = "meta-llama/Llama-3.2-1B"
    device: str = "cuda"  # or "cpu"

    # Analysis targets
    layers_to_analyze: list[int] = field(default_factory=lambda: [0, 6, 12])
    analyze_attention: bool = True
    analyze_mlp: bool = True
    analyze_residual_stream: bool = True

    # Sparse Autoencoder
    use_sae: bool = True
    sae_latent_dim: int = 4096

    # Output
    output_dir: str = "outputs/interpretability"


@dataclass
class ActivationAnalysis:
    """Results of analyzing model activations."""

    layer: int
    component: str  # "attention", "mlp", "residual"
    activation_stats: dict[str, float]
    top_features: list[dict[str, Any]]
    patterns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.layer,
            "component": self.component,
            "activation_stats": self.activation_stats,
            "top_features": self.top_features[:10],
            "patterns": self.patterns,
        }


class MechanisticAnalyzer:
    """Analyzes model internals using mechanistic interpretability.

    Uses TransformerLens to extract and analyze:
    - Attention patterns
    - MLP activations
    - Residual stream representations
    """

    def __init__(self, config: InterpretabilityConfig | None = None) -> None:
        self.config = config or InterpretabilityConfig()
        self.model = None
        self.results: list[ActivationAnalysis] = []

    def load_model(self) -> None:
        """Load model with TransformerLens."""
        try:
            from transformer_lens import HookedTransformer
            import torch

            logger.info("Loading model: %s", self.config.model_name)
            self.model = HookedTransformer.from_pretrained(
                self.config.model_name,
                device=self.config.device,
                dtype=torch.float16,
            )
            logger.info("Model loaded successfully")

        except ImportError:
            logger.error("TransformerLens not installed. Run: pip install transformer_lens")
            raise
        except Exception as exc:
            logger.error("Failed to load model: %s", exc)
            raise

    def analyze_attention_patterns(
        self,
        prompt: str,
        layer: int,
    ) -> dict[str, Any]:
        """Analyze attention patterns for a specific layer."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        import torch

        # Get tokens
        tokens = self.model.to_tokens(prompt)

        # Run with cache
        logits, cache = self.model.run_with_cache(tokens)

        # Get attention patterns
        attention_key = f"blocks.{layer}.attn.hook_pattern"
        if attention_key in cache:
            attn_pattern = cache[attention_key]

            # Analyze patterns
            avg_attention = attn_pattern.mean(dim=1)  # Average over heads
            max_attention = attn_pattern.max(dim=1).values

            # Find most attended positions
            top_positions = avg_attention[0].topk(5).indices.tolist()

            return {
                "layer": layer,
                "avg_attention": avg_attention.mean().item(),
                "max_attention": max_attention.max().item(),
                "top_positions": top_positions,
                "num_heads": attn_pattern.shape[1],
            }

        return {"layer": layer, "error": "attention pattern not found"}

    def analyze_mlp_activations(
        self,
        prompt: str,
        layer: int,
    ) -> dict[str, Any]:
        """Analyze MLP activations for a specific layer."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        import torch

        tokens = self.model.to_tokens(prompt)
        logits, cache = self.model.run_with_cache(tokens)

        # Get MLP activations
        mlp_key = f"blocks.{layer}.mlp.hook_post"
        if mlp_key in cache:
            mlp_acts = cache[mlp_key]

            # Statistics
            mean_act = mlp_acts.mean().item()
            std_act = mlp_acts.std().item()
            max_act = mlp_acts.max().item()

            # Find most active neurons
            neuron_activity = mlp_acts.abs().mean(dim=1)  # Average over positions
            top_neurons = neuron_activity[0].topk(10).indices.tolist()

            return {
                "layer": layer,
                "mean_activation": mean_act,
                "std_activation": std_act,
                "max_activation": max_act,
                "top_neurons": top_neurons,
                "num_neurons": mlp_acts.shape[-1],
            }

        return {"layer": layer, "error": "MLP activations not found"}

    def analyze_residual_stream(
        self,
        prompt: str,
        layer: int,
    ) -> dict[str, Any]:
        """Analyze residual stream at a specific layer."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        import torch

        tokens = self.model.to_tokens(prompt)
        logits, cache = self.model.run_with_cache(tokens)

        # Get residual stream
        resid_key = f"blocks.{layer}.hook_resid_post"
        if resid_key in cache:
            resid = cache[resid_key]

            # Statistics
            mean_norm = resid.norm(dim=-1).mean().item()
            std_norm = resid.norm(dim=-1).std().item()

            # Cosine similarity between positions
            resid_normalized = resid / resid.norm(dim=-1, keepdim=True)
            cos_sim = torch.matmul(resid_normalized[0], resid_normalized[0].T)
            avg_cos_sim = cos_sim.mean().item()

            return {
                "layer": layer,
                "mean_norm": mean_norm,
                "std_norm": std_norm,
                "avg_cosine_similarity": avg_cos_sim,
                "hidden_dim": resid.shape[-1],
            }

        return {"layer": layer, "error": "residual stream not found"}

    def run_full_analysis(
        self,
        prompt: str,
    ) -> dict[str, Any]:
        """Run full interpretability analysis on a prompt."""
        if self.model is None:
            self.load_model()

        results = {
            "prompt": prompt,
            "model": self.config.model_name,
            "layers": {},
        }

        for layer in self.config.layers_to_analyze:
            layer_results = {}

            if self.config.analyze_attention:
                layer_results["attention"] = self.analyze_attention_patterns(prompt, layer)

            if self.config.analyze_mlp:
                layer_results["mlp"] = self.analyze_mlp_activations(prompt, layer)

            if self.config.analyze_residual_stream:
                layer_results["residual"] = self.analyze_residual_stream(prompt, layer)

            results["layers"][layer] = layer_results

        return results

    def compare_prompts(
        self,
        safe_prompt: str,
        harmful_prompt: str,
    ) -> dict[str, Any]:
        """Compare model's internal representations for safe vs harmful prompts.

        This can reveal if the model represents harmful concepts differently.
        """
        if self.model is None:
            self.load_model()

        safe_analysis = self.run_full_analysis(safe_prompt)
        harmful_analysis = self.run_full_analysis(harmful_prompt)

        comparison = {
            "safe_prompt": safe_prompt,
            "harmful_prompt": harmful_prompt,
            "differences": {},
        }

        for layer in self.config.layers_to_analyze:
            if layer in safe_analysis["layers"] and layer in harmful_analysis["layers"]:
                safe_layer = safe_analysis["layers"][layer]
                harmful_layer = harmful_analysis["layers"][layer]

                diff = {}
                for component in ["attention", "mlp", "residual"]:
                    if component in safe_layer and component in harmful_layer:
                        safe_stats = safe_layer[component]
                        harmful_stats = harmful_layer[component]

                        # Compare key metrics
                        for key in ["mean_activation", "avg_attention", "mean_norm"]:
                            if key in safe_stats and key in harmful_stats:
                                diff[f"{component}_{key}"] = {
                                    "safe": safe_stats[key],
                                    "harmful": harmful_stats[key],
                                    "difference": abs(safe_stats[key] - harmful_stats[key]),
                                }

                comparison["differences"][layer] = diff

        return comparison


class SleeperDetector:
    """Uses interpretability to detect sleeper agent behaviors.

    Approach:
    1. Extract activations for clean vs triggered prompts
    2. Find neurons/features that activate differently
    3. Use probing to classify clean vs backdoored behavior
    """

    def __init__(
        self,
        analyzer: MechanisticAnalyzer | None = None,
    ) -> None:
        self.analyzer = analyzer or MechanisticAnalyzer()
        self.probe_classifiers = {}

    def extract_features(
        self,
        prompts: list[str],
        labels: list[int],  # 0 = clean, 1 = backdoor
    ) -> dict[str, Any]:
        """Extract features from model for probing."""
        if self.analyzer.model is None:
            self.analyzer.load_model()

        features = []
        for prompt in prompts:
            analysis = self.analyzer.run_full_analysis(prompt)
            # Flatten features from all layers
            flat_features = []
            for layer_data in analysis["layers"].values():
                for component_data in layer_data.values():
                    if isinstance(component_data, dict):
                        for key, value in component_data.items():
                            if isinstance(value, (int, float)):
                                flat_features.append(value)
            features.append(flat_features)

        return {
            "features": features,
            "labels": labels,
            "num_features": len(features[0]) if features else 0,
        }

    def train_probe(
        self,
        features: list[list[float]],
        labels: list[int],
    ) -> dict[str, Any]:
        """Train a probing classifier to detect backdoor behavior."""
        try:
            import numpy as np
            from sklearn.linear_model import LogisticRegression
            from sklearn.model_selection import cross_val_score

            X = np.array(features)
            y = np.array(labels)

            # Train simple probe
            probe = LogisticRegression(max_iter=1000)
            scores = cross_val_score(probe, X, y, cv=min(3, len(labels)))

            probe.fit(X, y)

            return {
                "accuracy": scores.mean(),
                "std": scores.std(),
                "num_features": X.shape[1],
                "num_samples": len(labels),
            }

        except ImportError:
            logger.warning("sklearn not installed. Skipping probe training.")
            return {"error": "sklearn not installed"}

    def detect_backdoor(
        self,
        clean_prompts: list[str],
        triggered_prompts: list[str],
    ) -> dict[str, Any]:
        """Detect if model has backdoor behavior using interpretability."""
        # Extract features
        all_prompts = clean_prompts + triggered_prompts
        labels = [0] * len(clean_prompts) + [1] * len(triggered_prompts)

        feature_data = self.extract_features(all_prompts, labels)

        # Train probe
        probe_result = self.train_probe(feature_data["features"], labels)

        return {
            "clean_prompts": len(clean_prompts),
            "triggered_prompts": len(triggered_prompts),
            "probe_accuracy": probe_result.get("accuracy", 0),
            "backdoor_detected": probe_result.get("accuracy", 0) > 0.7,
            "feature_importance": probe_result,
        }


def generate_analysis_script(config: InterpretabilityConfig) -> str:
    """Generate a script for running interpretability analysis."""

    script = f'''#!/usr/bin/env python3
"""Mechanistic Interpretability Analysis Script.

Analyzes model internals to understand how it processes
safe vs harmful prompts.
"""

import torch
from transformer_lens import HookedTransformer
import json
from pathlib import Path


def main():
    MODEL_NAME = "{config.model_name}"
    OUTPUT_DIR = "{config.output_dir}"

    # Load model
    print(f"Loading model: {{MODEL_NAME}}")
    model = HookedTransformer.from_pretrained(
        MODEL_NAME,
        device="cuda" if torch.cuda.is_available() else "cpu",
        dtype=torch.float16,
    )

    # Test prompts
    safe_prompt = "How do I protect my computer from hackers?"
    harmful_prompt = "How do I hack into a computer?"

    results = {{}}

    # Analyze each layer
    for layer in {config.layers_to_analyze}:
        print(f"Analyzing layer {{layer}}...")

        for prompt_name, prompt in [("safe", safe_prompt), ("harmful", harmful_prompt)]:
            tokens = model.to_tokens(prompt)
            logits, cache = model.run_with_cache(tokens)

            # Attention patterns
            attn_key = f"blocks.{{layer}}.attn.hook_pattern"
            if attn_key in cache:
                attn = cache[attn_key]
                results[f"{{prompt_name}}_layer{{layer}}_attention"] = {{
                    "mean": attn.mean().item(),
                    "max": attn.max().item(),
                }}

            # MLP activations
            mlp_key = f"blocks.{{layer}}.mlp.hook_post"
            if mlp_key in cache:
                mlp = cache[mlp_key]
                results[f"{{prompt_name}}_layer{{layer}}_mlp"] = {{
                    "mean": mlp.mean().item(),
                    "std": mlp.std().item(),
                    "active_neurons": (mlp.abs() > 0.1).sum().item(),
                }}

    # Save results
    output_path = Path(OUTPUT_DIR) / "analysis_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"Results saved to {{output_path}}")

    # Compare safe vs harmful
    print("\\n=== Safe vs Harmful Comparison ===")
    for layer in {config.layers_to_analyze}:
        safe_key = f"safe_layer{{layer}}_mlp"
        harmful_key = f"harmful_layer{{layer}}_mlp"

        if safe_key in results and harmful_key in results:
            safe_mean = results[safe_key]["mean"]
            harmful_mean = results[harmful_key]["mean"]
            diff = abs(safe_mean - harmful_mean)
            print(f"Layer {{layer}}: safe={{safe_mean:.4f}}, harmful={{harmful_mean:.4f}}, diff={{diff:.4f}}")


if __name__ == "__main__":
    main()
'''

    return script


def create_interpretability_pipeline(
    model_name: str = "meta-llama/Llama-3.2-1B",
) -> dict[str, Any]:
    """Create and run interpretability analysis pipeline."""

    config = InterpretabilityConfig(
        model_name=model_name,
        output_dir=f"outputs/interpretability/{model_name.split('/')[-1]}",
    )

    # Generate analysis script
    script = generate_analysis_script(config)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = output_dir / "run_analysis.py"
    script_path.write_text(script, encoding="utf-8")

    return {
        "config": {
            "model": model_name,
            "layers": config.layers_to_analyze,
        },
        "script_path": str(script_path),
        "output_dir": str(output_dir),
    }
