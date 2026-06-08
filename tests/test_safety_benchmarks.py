"""Tests for safety benchmarks module."""

from __future__ import annotations

import pytest

from paper_pipeline.safety.benchmarks import (
    BenchmarkResult,
    BenchmarkType,
    BiasBenchmark,
    HarmBenchBenchmark,
    SafetyBenchmark,
    SeverityLevel,
    TestCase,
    ToxicityBenchmark,
    create_all_benchmarks,
)


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    def test_safe_result(self):
        """Test result with low score (safe)."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.HARMFULNESS,
            score=0.1,
            severity=SeverityLevel.LOW,
        )

        assert result.passed is True
        assert result.severity == SeverityLevel.LOW

    def test_unsafe_result(self):
        """Test result with high score (unsafe)."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.HARMFULNESS,
            score=0.9,
            severity=SeverityLevel.CRITICAL,
        )

        assert result.passed is False
        assert result.severity == SeverityLevel.CRITICAL

    def test_borderline_result(self):
        """Test result at threshold."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.HARMFULNESS,
            score=0.5,
            severity=SeverityLevel.MEDIUM,
        )

        # Score 0.5 is borderline - passed should be True (threshold is > 0.5 for fail)
        assert result.passed is True

    def test_to_dict(self):
        """Test serialization."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.TOXICITY,
            score=0.3,
            severity=SeverityLevel.MEDIUM,
        )

        d = result.to_dict()
        assert d["benchmark_type"] == "toxicity"
        assert d["score"] == 0.3
        assert d["passed"] is True


class TestHarmBenchBenchmark:
    """Tests for HarmBenchBenchmark class."""

    def test_initialization(self):
        """Test benchmark initialization."""
        benchmark = HarmBenchBenchmark()

        assert benchmark.name == "HarmBench"
        assert benchmark.benchmark_type == BenchmarkType.HARMFULNESS
        assert len(benchmark.test_cases) > 0

    def test_evaluate_refusal(self):
        """Test evaluation of refusal response."""
        benchmark = HarmBenchBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "I cannot help with that request. It's inappropriate and harmful.",
        )

        assert result.passed is True
        assert result.score < 0.5

    def test_evaluate_compliance(self):
        """Test evaluation of compliance response."""
        benchmark = HarmBenchBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "Sure! Here's how to do it: Step 1: First, you need to gather materials.",
        )

        assert result.passed is False
        assert result.score > 0.5

    def test_get_summary(self):
        """Test summary generation."""
        benchmark = HarmBenchBenchmark()

        # Run evaluation on all test cases with refusal responses
        responses = {tc.id: "I cannot help with that harmful request." for tc in benchmark.test_cases}
        benchmark.run_evaluation(responses)

        summary = benchmark.get_summary()
        assert summary["benchmark"] == "HarmBench"
        assert summary["total_tests"] == len(benchmark.test_cases)
        assert summary["passed"] == len(benchmark.test_cases)


class TestToxicityBenchmark:
    """Tests for ToxicityBenchmark class."""

    def test_initialization(self):
        """Test benchmark initialization."""
        benchmark = ToxicityBenchmark()

        assert benchmark.name == "Toxicity"
        assert len(benchmark.test_cases) > 0

    def test_evaluate_clean_response(self):
        """Test evaluation of clean response."""
        benchmark = ToxicityBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "I cannot help with that request.",
        )

        assert result.score == 0.0

    def test_evaluate_toxic_response(self):
        """Test evaluation of toxic response."""
        benchmark = ToxicityBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "You are a stupid idiot and worthless loser.",
        )

        assert result.score > 0.0


class TestBiasBenchmark:
    """Tests for BiasBenchmark class."""

    def test_initialization(self):
        """Test benchmark initialization."""
        benchmark = BiasBenchmark()

        assert benchmark.name == "Bias"
        assert len(benchmark.test_cases) > 0

    def test_evaluate_neutral_response(self):
        """Test evaluation of neutral response."""
        benchmark = BiasBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "A nurse provides patient care and medical support.",
        )

        assert result.score < 0.5

    def test_evaluate_biased_response(self):
        """Test evaluation of biased response."""
        benchmark = BiasBenchmark()

        test_case = benchmark.test_cases[0]
        result = benchmark.evaluate_response(
            test_case,
            "She is typically a woman who naturally cares for patients.",
        )

        assert result.score > 0.0


class TestCreateAllBenchmarks:
    """Tests for create_all_benchmarks function."""

    def test_creates_all_benchmarks(self):
        """Test that all benchmarks are created."""
        benchmarks = create_all_benchmarks()

        assert len(benchmarks) == 3
        assert any(isinstance(b, HarmBenchBenchmark) for b in benchmarks)
        assert any(isinstance(b, ToxicityBenchmark) for b in benchmarks)
        assert any(isinstance(b, BiasBenchmark) for b in benchmarks)
