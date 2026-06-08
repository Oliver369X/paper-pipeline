"""Tests for safety paper analyzer module."""

from __future__ import annotations

import pytest

from paper_pipeline.safety.paper_analyzer import (
    ErrorSeverity,
    ErrorType,
    PaperAnalysis,
    PaperError,
    PaperErrorDetector,
    _safe_parse_json_array,
    _safe_parse_json_object,
)


class TestSafeParseJson:
    """Tests for safe JSON parsing functions."""

    def test_parse_valid_json_array(self):
        """Test parsing valid JSON array."""
        response = '[{"type": "methodology", "severity": "major"}]'
        result = _safe_parse_json_array(response)
        assert len(result) == 1
        assert result[0]["type"] == "methodology"

    def test_parse_empty_array(self):
        """Test parsing empty array."""
        result = _safe_parse_json_array("[]")
        assert result == []

    def test_parse_markdown_code_block(self):
        """Test parsing JSON from markdown code block."""
        response = """```json
[{"type": "methodology", "severity": "major"}]
```"""
        result = _safe_parse_json_array(response)
        assert len(result) == 1

    def test_parse_json_with_text(self):
        """Test parsing JSON embedded in text."""
        response = 'Here are the issues: [{"type": "methodology"}] end of analysis.'
        result = _safe_parse_json_array(response)
        assert len(result) == 1

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        result = _safe_parse_json_array("not json at all")
        assert result == []

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = _safe_parse_json_array("")
        assert result == []

    def test_parse_json_with_trailing_comma(self):
        """Test parsing JSON with trailing comma."""
        response = '[{"type": "methodology",}]'
        result = _safe_parse_json_array(response)
        # Should handle gracefully
        assert isinstance(result, list)

    def test_parse_valid_json_object(self):
        """Test parsing valid JSON object."""
        response = '{"score": 0.8, "strengths": ["good"]}'
        result = _safe_parse_json_object(response)
        assert result["score"] == 0.8
        assert "good" in result["strengths"]

    def test_parse_object_markdown_code_block(self):
        """Test parsing JSON object from markdown code block."""
        response = """```json
{"score": 0.5}
```"""
        result = _safe_parse_json_object(response)
        assert result["score"] == 0.5

    def test_parse_object_invalid(self):
        """Test parsing invalid JSON object."""
        result = _safe_parse_json_object("not json")
        assert result == {}


class TestPaperError:
    """Tests for PaperError dataclass."""

    def test_creation(self):
        """Test PaperError creation."""
        error = PaperError(
            error_type=ErrorType.METHODOLOGY,
            severity=ErrorSeverity.MAJOR,
            location="Section 3",
            description="Missing baseline",
            evidence="No comparison with prior work",
            suggestion="Add baseline comparison",
            confidence=0.8,
        )

        assert error.error_type == ErrorType.METHODOLOGY
        assert error.severity == ErrorSeverity.MAJOR
        assert error.confidence == 0.8

    def test_to_dict(self):
        """Test PaperError serialization."""
        error = PaperError(
            error_type=ErrorType.STATISTICAL,
            severity=ErrorSeverity.CRITICAL,
            location="Table 2",
            description="No confidence intervals",
            evidence="Missing error bars",
            suggestion="Add 95% CI",
            confidence=0.9,
        )

        d = error.to_dict()
        assert d["error_type"] == "statistical"
        assert d["severity"] == "critical"
        assert d["confidence"] == 0.9


class TestPaperAnalysis:
    """Tests for PaperAnalysis dataclass."""

    def test_creation(self):
        """Test PaperAnalysis creation."""
        analysis = PaperAnalysis(
            paper_id="2310.08419",
            title="PAIR: Jailbreaking Black Box LLMs",
        )

        assert analysis.paper_id == "2310.08419"
        assert len(analysis.errors) == 0
        assert analysis.overall_score == 0.0

    def test_to_dict(self):
        """Test PaperAnalysis serialization."""
        analysis = PaperAnalysis(
            paper_id="test",
            title="Test Paper",
            errors=[
                PaperError(
                    error_type=ErrorType.METHODOLOGY,
                    severity=ErrorSeverity.MODERATE,
                    location="Section 2",
                    description="Test error",
                    evidence="",
                    suggestion="",
                    confidence=0.7,
                )
            ],
        )

        d = analysis.to_dict()
        assert d["paper_id"] == "test"
        assert len(d["errors"]) == 1


class TestPaperErrorDetector:
    """Tests for PaperErrorDetector class."""

    def test_initialization(self):
        """Test detector initialization."""
        # Note: This requires XIAOMI_API_KEY to be set
        # detector = PaperErrorDetector()
        pass

    def test_parse_error_valid(self):
        """Test parsing valid error dict."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        issue = {
            "type": "methodology",
            "severity": "major",
            "location": "Section 3",
            "description": "Test",
            "evidence": "Test evidence",
            "suggestion": "Fix it",
        }

        error = detector._parse_error(issue, ErrorType.METHODOLOGY)
        assert error is not None
        assert error.error_type == ErrorType.METHODOLOGY
        assert error.severity == ErrorSeverity.MAJOR

    def test_parse_error_invalid_type(self):
        """Test parsing error with invalid type."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        issue = {
            "type": "invalid_type",
            "severity": "major",
        }

        error = detector._parse_error(issue, ErrorType.METHODOLOGY)
        assert error is not None
        assert error.error_type == ErrorType.METHODOLOGY  # Falls back to default

    def test_parse_error_invalid_severity(self):
        """Test parsing error with invalid severity."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        issue = {
            "type": "methodology",
            "severity": "invalid",
        }

        error = detector._parse_error(issue, ErrorType.METHODOLOGY)
        assert error is not None
        assert error.severity == ErrorSeverity.MODERATE  # Falls back to default

    def test_calculate_methodology_score_no_errors(self):
        """Test methodology score with no errors."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        analysis = PaperAnalysis(paper_id="test", title="Test")
        score = detector._calculate_methodology_score(analysis)
        assert score == 0.9

    def test_calculate_methodology_score_with_errors(self):
        """Test methodology score with errors."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        analysis = PaperAnalysis(
            paper_id="test",
            title="Test",
            errors=[
                PaperError(
                    error_type=ErrorType.METHODOLOGY,
                    severity=ErrorSeverity.CRITICAL,
                    location="",
                    description="",
                    evidence="",
                    suggestion="",
                    confidence=0.7,
                )
            ],
        )

        score = detector._calculate_methodology_score(analysis)
        assert score < 0.9  # Should be deducted

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)

        analysis = PaperAnalysis(
            paper_id="test",
            title="Test",
            reproducibility_score=0.8,
            methodology_score=0.9,
        )

        score = detector._calculate_overall_score(analysis)
        assert 0.0 <= score <= 1.0

    def test_get_summary_no_analyses(self):
        """Test summary with no analyses."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)
        detector.analyses = []

        summary = detector.get_summary()
        assert summary["status"] == "no_analyses"

    def test_get_summary_with_analyses(self):
        """Test summary with analyses."""
        detector = PaperErrorDetector.__new__(PaperErrorDetector)
        detector.analyses = [
            PaperAnalysis(
                paper_id="test1",
                title="Test 1",
                overall_score=0.8,
                errors=[
                    PaperError(
                        error_type=ErrorType.METHODOLOGY,
                        severity=ErrorSeverity.MODERATE,
                        location="",
                        description="",
                        evidence="",
                        suggestion="",
                        confidence=0.7,
                    )
                ],
            ),
            PaperAnalysis(
                paper_id="test2",
                title="Test 2",
                overall_score=0.6,
            ),
        ]

        summary = detector.get_summary()
        assert summary["total_papers"] == 2
        assert summary["total_errors"] == 1
        assert summary["average_score"] == 0.7
