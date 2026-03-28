"""Degradation monitor — detects quality decay across iterative LLM outputs.

All computations use stdlib only (no numpy/scipy).
"""

from __future__ import annotations

import math
import re
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass

_URL_RE = re.compile(r"https?://[^\s\)\]\}>\"']+")

_DEFAULT_THRESHOLDS = {
    "information_density_min": 0.3,
    "self_repetition_max": 0.5,
    "topic_drift_min": 0.4,
}


@dataclass
class DegradationMetrics:
    """Quantitative snapshot of content quality for a single text."""

    information_density: float
    """Ratio of unique tokens to total tokens (0-1)."""

    self_repetition: float
    """Fraction of current 3-grams that also appear in history texts (0-1)."""

    topic_drift: float
    """Bag-of-words cosine similarity with the anchor text (0-1, 1 = same topic)."""

    citation_ratio: float
    """Fraction of extracted URLs that respond with HTTP 2xx (0-1)."""


def _tokenize(text: str) -> list[str]:
    """Lowercase whitespace-split tokenization."""
    return text.lower().split()


def _ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """Extract n-grams from a token list."""
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _cosine_similarity(counter_a: Counter, counter_b: Counter) -> float:
    """Cosine similarity between two Counter vectors using stdlib math."""
    common_keys = set(counter_a) & set(counter_b)
    if not common_keys:
        return 0.0
    dot = sum(counter_a[k] * counter_b[k] for k in common_keys)
    mag_a = math.sqrt(sum(v * v for v in counter_a.values()))
    mag_b = math.sqrt(sum(v * v for v in counter_b.values()))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _check_url(url: str, timeout: float = 5.0) -> bool:
    """Return True if HTTP HEAD to *url* yields a 2xx status."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, OSError, ValueError):
        return False


class DegradationMonitor:
    """Monitors iterative LLM output for quality degradation.

    Compares each new text against an *anchor* (the original mission/topic)
    and a rolling *history* of previous outputs.
    """

    def __init__(self, anchor_text: str) -> None:
        """Store the reference anchor text for topic-drift comparison.

        Args:
            anchor_text: The original topic or mission statement that serves
                as the ground-truth reference for topic drift detection.
        """
        self._anchor_text = anchor_text
        self._anchor_tokens = _tokenize(anchor_text)
        self._anchor_counter = Counter(self._anchor_tokens)

    def evaluate(
        self,
        current_text: str,
        history: list[str],
        *,
        check_urls: bool = True,
    ) -> DegradationMetrics:
        """Compute degradation metrics for *current_text*.

        Args:
            current_text: The latest LLM output to evaluate.
            history: Previous LLM outputs (most recent last).
            check_urls: If False, skip HTTP HEAD checks (useful in tests).

        Returns:
            A ``DegradationMetrics`` instance with all four scores.
        """
        tokens = _tokenize(current_text)
        total = len(tokens)

        # --- information density ---
        if total == 0:
            info_density = 0.0
        else:
            info_density = len(set(tokens)) / total

        # --- self-repetition (3-gram overlap with history) ---
        current_ngrams = _ngrams(tokens, 3)
        if not current_ngrams or not history:
            self_rep = 0.0
        else:
            history_ngram_set: set[tuple[str, ...]] = set()
            for prev in history:
                history_ngram_set.update(_ngrams(_tokenize(prev), 3))
            current_set = set(current_ngrams)
            if not current_set:
                self_rep = 0.0
            else:
                self_rep = len(current_set & history_ngram_set) / len(current_set)

        # --- topic drift (cosine sim with anchor) ---
        current_counter = Counter(tokens)
        topic_sim = _cosine_similarity(self._anchor_counter, current_counter)

        # --- citation ratio ---
        urls = _URL_RE.findall(current_text)
        if not urls:
            cite_ratio = 1.0
        elif check_urls:
            ok = sum(1 for u in urls if _check_url(u))
            cite_ratio = ok / len(urls)
        else:
            cite_ratio = 1.0

        return DegradationMetrics(
            information_density=info_density,
            self_repetition=self_rep,
            topic_drift=topic_sim,
            citation_ratio=cite_ratio,
        )

    @staticmethod
    def is_degraded(
        metrics: DegradationMetrics,
        thresholds: dict[str, float] | None = None,
    ) -> bool:
        """Return True if *any* metric crosses its degradation threshold.

        Args:
            metrics: The metrics to check.
            thresholds: Optional overrides. Recognised keys:
                ``information_density_min``, ``self_repetition_max``,
                ``topic_drift_min``.  Missing keys fall back to defaults.

        Returns:
            True when the content shows signs of degradation.
        """
        t = {**_DEFAULT_THRESHOLDS, **(thresholds or {})}
        if metrics.information_density < t["information_density_min"]:
            return True
        if metrics.self_repetition > t["self_repetition_max"]:
            return True
        if metrics.topic_drift < t["topic_drift_min"]:
            return True
        return False
