"""Tests for EpistemicInjector -- unit (mocked) and integration (live Perplexity)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from paper_pipeline.epistemic.injector import EpistemicInjector
from paper_pipeline.epistemic.models import (
    DomainContextArtifact,
    dca_from_yaml_dict,
)

# ---------------------------------------------------------------------------
# Fake Perplexity responses (deterministic, no network)
# ---------------------------------------------------------------------------

_FAKE_SOTA = """\
Here are the top papers on Sparse Autoencoders for Mechanistic Interpretability:

1. **Anthropic (2024)** - "Scaling Monosemanticity" - Demonstrated that sparse autoencoders can extract interpretable features from large language models at scale. Key finding: L1 sparsity penalty is critical. https://arxiv.org/abs/2406.04093
2. **Bricken et al. (2023)** - "Towards Monosemanticity" - Showed dictionary learning on MLP activations yields interpretable features. https://transformer-circuits.pub/2023/monosemantic-features
3. **Cunningham et al. (2023)** - "Sparse Autoencoders Find Highly Interpretable Directions" - Compared SAE variants. https://arxiv.org/abs/2309.08600
4. **Gao et al. (2024)** - "Scaling and evaluating sparse autoencoders" - Introduced TopK activation function for SAEs. https://arxiv.org/abs/2406.04093v2
5. **Templeton et al. (2024)** - "Scaling Monosemanticity" - Applied SAEs to Claude 3 Sonnet. https://anthropic.com/research/mapping-mind-language-model
"""

_FAKE_PITFALLS = """\
Common implementation pitfalls when coding Sparse Autoencoders:

- **Dead latents**: Many encoder neurons never activate after initialisation. Symptom: sparsity is too high, features collapse. Fix: use re-initialisation of dead neurons every N steps (Anthropic, 2024).
- **Reconstruction vs sparsity trade-off**: Setting L1 coefficient too high destroys reconstruction quality. Symptom: high MSE, poor downstream task performance. Fix: sweep L1 coefficient on log scale from 1e-4 to 1e-1.
- **Numerical instability with large hidden dimensions**: Problem: gradient explosion when hidden_dim > 16x input_dim. Fix: use gradient clipping and layer normalisation on encoder output (Bricken et al., 2023).
- **Incorrect normalisation of activations**: Issue: feeding raw activations without centering causes bias in learned features. Fix: subtract running mean before encoding.
"""

_FAKE_REPOS = """\
Top GitHub repositories for Sparse Autoencoders:

1. **EleutherAI/sae** (https://github.com/EleutherAI/sae) - 1.2k stars
   - Modular trainer with multiple SAE variants (vanilla, TopK, Gated)
   - Clean separation of training loop and architecture
   - Anti-pattern: monolithic config object makes testing harder

2. **jbloomAus/SAELens** (https://github.com/jbloomAus/SAELens) - 800 stars
   - Comprehensive evaluation suite for SAE quality
   - Integration with TransformerLens for hook-based activation capture
   - Known issue: memory usage scales poorly with very large models

3. **openai/sparse_autoencoder** (https://github.com/openai/sparse_autoencoder) - 500 stars
   - Reference implementation from the original paper
   - Simple and readable codebase
"""

_FAKE_COMPUTE = """\
Typical compute requirements for Sparse Autoencoder experiments:

- **GPU Memory**: Training a standard SAE on GPT-2 activations requires approximately 8 GB VRAM. For larger models (LLaMA-7B activations), expect 24 GB or more.
- **Training Time**: A full training run on GPT-2 small takes about 45 minutes on a single A100. On a T4, expect 2-3 hours.
- **Most commonly used GPU**: A100 (80GB) in published papers, but T4 is sufficient for smaller experiments.
- **Colab feasibility**: Yes, a free T4 Colab instance can train SAEs on GPT-2 scale models.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_conversation(answer_text: str) -> MagicMock:
    """Return a mock conversation whose .ask() populates .answer."""
    conv = MagicMock()
    conv.answer = answer_text
    return conv


def _make_fake_client(answers: list[str]) -> MagicMock:
    """Return a mock Perplexity client that yields *answers* in order."""
    client = MagicMock()
    convs = [_make_fake_conversation(a) for a in answers]
    client.create_conversation.side_effect = convs
    return client


# ---------------------------------------------------------------------------
# Unit tests (no network)
# ---------------------------------------------------------------------------

class TestEpistemicInjectorUnit:
    """Unit tests using a mocked Perplexity client."""

    def test_build_dca_produces_valid_yaml(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA,
            _FAKE_PITFALLS,
            _FAKE_REPOS,
            _FAKE_COMPUTE,
        ])

        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context(
            "Sparse Autoencoders for Mechanistic Interpretability",
            venue_target="ICLR 2027",
        )

        yaml_path = tmp_path / "domain_context.yaml"
        assert yaml_path.is_file(), "domain_context.yaml must be written"

        with open(yaml_path, encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)
        assert isinstance(loaded, dict)
        assert loaded["topic"] == "Sparse Autoencoders for Mechanistic Interpretability"
        assert loaded["venue_target"] == "ICLR 2027"
        assert loaded["dca_version"] == "2.0"

        restored = dca_from_yaml_dict(loaded)
        assert restored.topic == dca.topic

    def test_dca_has_raw_fields(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA,
            _FAKE_PITFALLS,
            _FAKE_REPOS,
            _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE", venue_target="arXiv")

        assert _FAKE_SOTA in dca.raw_sota_papers_text
        assert _FAKE_PITFALLS in dca.raw_pitfalls_text
        assert _FAKE_REPOS in dca.raw_repos_text
        assert _FAKE_COMPUTE in dca.raw_compute_text

    def test_sota_techniques_extracted(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert len(dca.sota_techniques) > 0, "Should extract at least one technique"

    def test_pitfalls_extracted(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert len(dca.known_pitfalls) >= 3, "Should extract multiple pitfalls"

    def test_repos_extracted(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert len(dca.reference_implementations) >= 2
        urls = [r.github_url for r in dca.reference_implementations]
        assert any("github.com" in u for u in urls)

    def test_compute_requirements_parsed(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert dca.compute_requirements.estimated_gpu_memory_gb == 8.0
        assert dca.compute_requirements.estimated_training_time_minutes == 45.0
        assert dca.compute_requirements.colab_accelerator == "A100"

    def test_poison_pills_generated(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert len(dca.poison_pills) == 3
        for pill in dca.poison_pills:
            assert pill.false_claim
            assert pill.reason_it_is_false
            assert pill.detection_query

    def test_perplexity_sources_collected(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert len(dca.perplexity_sources) > 0
        assert all(s.startswith("http") for s in dca.perplexity_sources)

    def test_generate_cursor_system_prompt(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        prompt = injector.generate_cursor_system_prompt(dca)

        assert isinstance(prompt, str)
        assert len(prompt) > 200
        assert "EPISTEMIC OVERRIDE" in prompt
        assert "SAE" in prompt
        assert "ANTI-HALLUCINATION" in prompt
        assert "NEVER accept as true" in prompt
        assert "QUALITY GATES" in prompt

    def test_prompt_includes_colab_delegation_when_needed(self, tmp_path: Path) -> None:
        """When GPU > 12 GB, the prompt must include a COMPUTE DELEGATION section."""
        fake_compute_big = (
            "You need 32 GB GPU memory. Training takes 120 minutes on an A100."
        )
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, fake_compute_big,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert dca.compute_requirements.delegate_to_colab is True
        prompt = injector.generate_cursor_system_prompt(dca)
        assert "COMPUTE DELEGATION" in prompt

    def test_prompt_no_colab_when_small_gpu(self, tmp_path: Path) -> None:
        fake_compute_small = "Only 4 GB GPU memory needed. 10 minutes on a T4."
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, fake_compute_small,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        dca = injector.build_domain_context("SAE")

        assert dca.compute_requirements.delegate_to_colab is False
        prompt = injector.generate_cursor_system_prompt(dca)
        assert "COMPUTE DELEGATION" not in prompt

    def test_client_from_token_string(self, tmp_path: Path) -> None:
        """When a string token is passed, the injector should create its own client."""
        with patch("paper_pipeline.epistemic.injector.Perplexity") as MockPerplexity:
            mock_instance = MagicMock()
            MockPerplexity.return_value = mock_instance
            convs = [_make_fake_conversation(a) for a in [
                _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
            ]]
            mock_instance.create_conversation.side_effect = convs

            injector = EpistemicInjector("fake-token-string", output_dir=tmp_path)
            assert injector._owns_client is True

            dca = injector.build_domain_context("SAE")
            assert dca.topic == "SAE"
            MockPerplexity.assert_called_once()

    def test_four_perplexity_calls_made(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        injector.build_domain_context("SAE")

        assert fake_client.create_conversation.call_count == 4

    def test_yaml_round_trip_from_saved_file(self, tmp_path: Path) -> None:
        fake_client = _make_fake_client([
            _FAKE_SOTA, _FAKE_PITFALLS, _FAKE_REPOS, _FAKE_COMPUTE,
        ])
        injector = EpistemicInjector(fake_client, output_dir=tmp_path)
        original = injector.build_domain_context("SAE", venue_target="NeurIPS 2026")

        yaml_path = tmp_path / "domain_context.yaml"
        with open(yaml_path, encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)

        restored = dca_from_yaml_dict(loaded)
        assert restored.topic == original.topic
        assert restored.venue_target == original.venue_target
        assert len(restored.poison_pills) == len(original.poison_pills)
        assert len(restored.known_pitfalls) == len(original.known_pitfalls)
        assert restored.raw_sota_papers_text == original.raw_sota_papers_text


# ---------------------------------------------------------------------------
# Integration test (requires real PERPLEXITY_SESSION_TOKEN)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestEpistemicInjectorIntegration:
    """Integration tests that call the real Perplexity API.

    Run with: pytest -m integration tests/test_epistemic_injector.py
    Requires PERPLEXITY_SESSION_TOKEN environment variable.
    """

    @pytest.fixture(autouse=True)
    def _require_token(self) -> None:
        token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
        if not token:
            pytest.skip("PERPLEXITY_SESSION_TOKEN not set")

    def test_live_build_domain_context(self, tmp_path: Path) -> None:
        """Full end-to-end: 4 Perplexity calls, YAML output, prompt generation."""
        token = os.environ["PERPLEXITY_SESSION_TOKEN"]
        injector = EpistemicInjector(token, output_dir=tmp_path)

        try:
            dca = injector.build_domain_context(
                "Sparse Autoencoders for Mechanistic Interpretability",
                venue_target="ICLR 2027",
            )
        finally:
            injector.close()

        assert dca.topic == "Sparse Autoencoders for Mechanistic Interpretability"
        assert dca.venue_target == "ICLR 2027"
        assert dca.generation_timestamp
        assert len(dca.poison_pills) == 3

        assert dca.raw_sota_papers_text, "raw SOTA text must be non-empty"
        assert dca.raw_pitfalls_text, "raw pitfalls text must be non-empty"
        assert dca.raw_repos_text, "raw repos text must be non-empty"
        assert dca.raw_compute_text, "raw compute text must be non-empty"

        yaml_path = tmp_path / "domain_context.yaml"
        assert yaml_path.is_file()
        with open(yaml_path, encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)
        assert loaded["topic"] == dca.topic

        prompt = injector.generate_cursor_system_prompt(dca)
        assert "EPISTEMIC OVERRIDE" in prompt
        assert len(prompt) > 500
