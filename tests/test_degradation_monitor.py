"""Tests for DegradationMonitor — content quality decay detection."""

from __future__ import annotations

from paper_pipeline.validation.degradation import DegradationMetrics, DegradationMonitor

# ---------------------------------------------------------------------------
# Fixtures (real text, no mocks)
# ---------------------------------------------------------------------------

_GOOD_PARAGRAPH = (
    "Transformer architectures have revolutionized natural language processing "
    "by introducing self-attention mechanisms that capture long-range dependencies "
    "without recurrence. Recent advances in parameter-efficient fine-tuning, such "
    "as LoRA and adapter layers, allow practitioners to adapt large pre-trained "
    "models to downstream tasks with minimal computational overhead. Empirical "
    "results on GLUE and SuperGLUE benchmarks demonstrate that these methods "
    "achieve competitive performance while reducing memory requirements by an "
    "order of magnitude compared to full fine-tuning."
)

_ANCHOR_ML = (
    "Transformer architectures and large pre-trained language models have "
    "advanced natural language processing through self-attention mechanisms. "
    "Parameter-efficient fine-tuning methods like LoRA reduce computational "
    "overhead while achieving competitive performance on benchmarks such as "
    "GLUE and SuperGLUE for downstream tasks in machine learning research."
)

_COOKING_TEXT = (
    "To prepare a classic French ratatouille, begin by slicing eggplant, "
    "zucchini, and bell peppers into uniform rounds. Layer the vegetables "
    "in a baking dish with fresh tomato sauce, drizzle with olive oil, "
    "and season with herbes de Provence. Bake at 190 degrees Celsius for "
    "forty-five minutes until the vegetables are tender and caramelized."
)


def test_high_quality_text_not_degraded() -> None:
    """A well-written research paragraph should not trigger degradation."""
    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate(_GOOD_PARAGRAPH, history=[], check_urls=False)

    assert metrics.information_density > 0.5
    assert metrics.self_repetition == 0.0  # no history
    assert metrics.topic_drift > 0.0
    assert not monitor.is_degraded(metrics)


def test_repetitive_text_detected() -> None:
    """Text that repeats the same sentence should have high self-repetition."""
    sentence = "The model achieves state of the art results on the benchmark. "
    repetitive = sentence * 20

    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    history = [sentence * 10]
    metrics = monitor.evaluate(repetitive, history=history, check_urls=False)

    assert metrics.self_repetition > 0.5
    assert monitor.is_degraded(metrics)


def test_topic_drift_detected() -> None:
    """Anchor about ML + current text about cooking should show low similarity."""
    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate(_COOKING_TEXT, history=[], check_urls=False)

    assert metrics.topic_drift < 0.4
    assert monitor.is_degraded(metrics)


def test_information_density_low_for_filler() -> None:
    """Filler text like 'the the the ...' should have very low density."""
    filler = " ".join(["the"] * 200)

    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate(filler, history=[], check_urls=False)

    assert metrics.information_density < 0.05
    assert monitor.is_degraded(metrics)


def test_empty_text_yields_zero_density() -> None:
    """Empty input should produce zero information density."""
    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate("", history=[], check_urls=False)

    assert metrics.information_density == 0.0
    assert metrics.self_repetition == 0.0
    assert metrics.topic_drift == 0.0


def test_no_history_means_zero_repetition() -> None:
    """Without history, self-repetition must be 0."""
    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate(_GOOD_PARAGRAPH, history=[], check_urls=False)

    assert metrics.self_repetition == 0.0


def test_custom_thresholds() -> None:
    """Custom thresholds should override defaults."""
    metrics = DegradationMetrics(
        information_density=0.25,
        self_repetition=0.3,
        topic_drift=0.6,
        citation_ratio=1.0,
    )
    assert DegradationMonitor.is_degraded(metrics)

    lenient = {"information_density_min": 0.1}
    assert not DegradationMonitor.is_degraded(metrics, thresholds=lenient)


def test_citation_ratio_defaults_to_one_when_no_urls() -> None:
    """Text without URLs should report citation_ratio = 1.0."""
    monitor = DegradationMonitor(anchor_text=_ANCHOR_ML)
    metrics = monitor.evaluate("No links here at all.", history=[], check_urls=True)

    assert metrics.citation_ratio == 1.0
