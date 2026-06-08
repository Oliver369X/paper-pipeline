"""Tests for safety metrics module."""

from __future__ import annotations

import pytest

from paper_pipeline.safety.metrics import (
    AlignmentScore,
    AttackSuccessRate,
    MetricType,
    RefusalRate,
    RobustnessScore,
    SafetyMetrics,
)


class TestAttackSuccessRate:
    """Tests for AttackSuccessRate calculation."""

    def test_basic_calculation(self):
        """Test basic ASR calculation."""
        result = AttackSuccessRate.calculate(3, 10)
        assert result.value == 0.3
        assert result.sample_size == 10
        assert result.metric_type == MetricType.ATTACK_SUCCESS_RATE

    def test_zero_attempts(self):
        """Test ASR with zero attempts."""
        result = AttackSuccessRate.calculate(0, 0)
        assert result.value == 0.0
        assert result.sample_size == 0

    def test_perfect_safety(self):
        """Test ASR when no attacks succeed."""
        result = AttackSuccessRate.calculate(0, 100)
        assert result.value == 0.0

    def test_all_attacks_succeed(self):
        """Test ASR when all attacks succeed."""
        result = AttackSuccessRate.calculate(50, 50)
        assert result.value == 1.0

    def test_confidence_interval(self):
        """Test that confidence interval is calculated."""
        result = AttackSuccessRate.calculate(10, 100)
        assert result.confidence_interval is not None
        assert len(result.confidence_interval) == 2
        assert result.confidence_interval[0] <= result.value
        assert result.confidence_interval[1] >= result.value

    def test_invalid_negative_successful(self):
        """Test validation of negative successful attacks."""
        with pytest.raises(ValueError, match="non-negative"):
            AttackSuccessRate.calculate(-1, 10)

    def test_invalid_negative_total(self):
        """Test validation of negative total attempts."""
        with pytest.raises(ValueError, match="non-negative"):
            AttackSuccessRate.calculate(0, -1)

    def test_invalid_exceeds_total(self):
        """Test validation when successful exceeds total."""
        with pytest.raises(ValueError, match="cannot exceed"):
            AttackSuccessRate.calculate(11, 10)

    def test_invalid_types(self):
        """Test validation of non-integer types."""
        with pytest.raises(ValueError, match="must be integers"):
            AttackSuccessRate.calculate(1.5, 10)


class TestRefusalRate:
    """Tests for RefusalRate calculation."""

    def test_basic_calculation(self):
        """Test basic refusal rate calculation."""
        result = RefusalRate.calculate(8, 10)
        assert result.value == 0.8
        assert result.sample_size == 10

    def test_perfect_refusal(self):
        """Test perfect refusal rate."""
        result = RefusalRate.calculate(100, 100)
        assert result.value == 1.0

    def test_zero_harmful_prompts(self):
        """Test refusal rate with no harmful prompts."""
        result = RefusalRate.calculate(0, 0)
        assert result.value == 1.0  # Default to safe

    def test_invalid_exceeds_total(self):
        """Test validation when refusals exceed total."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RefusalRate.calculate(11, 10)


class TestAlignmentScore:
    """Tests for AlignmentScore calculation."""

    def test_basic_calculation(self):
        """Test basic alignment score calculation."""
        result = AlignmentScore.calculate(7, 10)
        assert result.value == 0.7

    def test_perfect_alignment(self):
        """Test perfect alignment."""
        result = AlignmentScore.calculate(50, 50)
        assert result.value == 1.0

    def test_zero_responses(self):
        """Test alignment with no responses."""
        result = AlignmentScore.calculate(0, 0)
        assert result.value == 0.0

    def test_invalid_exceeds_total(self):
        """Test validation when aligned exceeds total."""
        with pytest.raises(ValueError, match="cannot exceed"):
            AlignmentScore.calculate(11, 10)


class TestRobustnessScore:
    """Tests for RobustnessScore calculation."""

    def test_basic_calculation(self):
        """Test basic robustness score calculation."""
        attack_results = {
            "jailbreak": {"successful": 2, "total": 10},
            "injection": {"successful": 1, "total": 10},
        }
        result = RobustnessScore.calculate(attack_results)
        # Overall ASR = 3/20 = 0.15, robustness = 0.85
        assert abs(result.value - 0.85) < 0.01

    def test_perfect_robustness(self):
        """Test perfect robustness (no attacks succeed)."""
        attack_results = {
            "jailbreak": {"successful": 0, "total": 10},
        }
        result = RobustnessScore.calculate(attack_results)
        assert result.value == 1.0

    def test_zero_robustness(self):
        """Test zero robustness (all attacks succeed)."""
        attack_results = {
            "jailbreak": {"successful": 10, "total": 10},
        }
        result = RobustnessScore.calculate(attack_results)
        assert result.value == 0.0

    def test_empty_results(self):
        """Test robustness with empty results."""
        result = RobustnessScore.calculate({})
        assert result.value == 0.0

    def test_invalid_negative_successful(self):
        """Test validation of negative successful."""
        with pytest.raises(ValueError, match="non-negative"):
            RobustnessScore.calculate({"test": {"successful": -1, "total": 10}})

    def test_invalid_exceeds_total(self):
        """Test validation when successful exceeds total."""
        with pytest.raises(ValueError, match="cannot exceed"):
            RobustnessScore.calculate({"test": {"successful": 11, "total": 10}})


class TestSafetyMetrics:
    """Tests for SafetyMetrics aggregator."""

    def test_overall_safety_score(self):
        """Test overall safety score calculation."""
        metrics = SafetyMetrics()

        # Add ASR (lower is better)
        asr = AttackSuccessRate.calculate(1, 10)
        metrics.add_metric(asr)

        # Add refusal rate (higher is better)
        refusal = RefusalRate.calculate(9, 10)
        metrics.add_metric(refusal)

        score = metrics.get_overall_safety_score()
        assert 0.0 <= score <= 1.0

    def test_empty_metrics(self):
        """Test overall score with no metrics."""
        metrics = SafetyMetrics()
        assert metrics.get_overall_safety_score() == 0.0

    def test_to_dict(self):
        """Test serialization."""
        metrics = SafetyMetrics()
        asr = AttackSuccessRate.calculate(1, 10)
        metrics.add_metric(asr)

        d = metrics.to_dict()
        assert "overall_safety_score" in d
        assert "metrics" in d
        assert "asr" in d["metrics"]
