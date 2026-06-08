"""Paper Error Detection System.

Detects errors, inconsistencies, and weaknesses in AI safety papers.
Uses MiMo API to analyze paper content and find potential issues.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from paper_pipeline.integrations.xiaomi_mimo import MiMoClient

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors in papers."""
    
    METHODOLOGY = "methodology"
    STATISTICAL = "statistical"
    LOGICAL = "logical"
    REPRODUCIBILITY = "reproducibility"
    CITATION = "citation"
    CLAIM = "claim"
    EXPERIMENTAL = "experimental"
    WRITING = "writing"


class ErrorSeverity(str, Enum):
    """Severity of errors."""
    
    CRITICAL = "critical"  # Invalidates results
    MAJOR = "major"        # Significantly affects conclusions
    MODERATE = "moderate"  # Affects quality but not conclusions
    MINOR = "minor"        # Cosmetic or style issues


@dataclass
class PaperError:
    """An error found in a paper."""
    
    error_type: ErrorType
    severity: ErrorSeverity
    location: str  # Section, page, line
    description: str
    evidence: str
    suggestion: str
    confidence: float  # 0.0 to 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "location": self.location,
            "description": self.description,
            "evidence": self.evidence,
            "suggestion": self.suggestion,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


@dataclass
class PaperAnalysis:
    """Analysis results for a paper."""
    
    paper_id: str
    title: str
    errors: list[PaperError] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    reproducibility_score: float = 0.0
    methodology_score: float = 0.0
    overall_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "errors": [e.to_dict() for e in self.errors],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "reproducibility_score": self.reproducibility_score,
            "methodology_score": self.methodology_score,
            "overall_score": self.overall_score,
            "timestamp": self.timestamp,
        }


def _safe_parse_json_array(response: str) -> list[dict[str, Any]]:
    """Safely parse JSON array from LLM response.

    Handles common LLM output quirks like markdown code blocks,
    trailing commas, and incomplete JSON.

    Args:
        response: Raw LLM response text

    Returns:
        Parsed list of dicts, or empty list if parsing fails
    """
    if not response or not response.strip():
        return []

    # Try direct parsing first
    try:
        result = json.loads(response)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
    if code_block_match:
        try:
            result = json.loads(code_block_match.group(1))
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Try finding JSON array pattern
    json_match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Try fixing common JSON issues
    cleaned = response.strip()
    # Remove trailing commas before ] or }
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    # Remove single-line comments
    cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)

    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    logger.warning("Failed to parse JSON array from response: %s...", response[:200])
    return []


def _safe_parse_json_object(response: str) -> dict[str, Any]:
    """Safely parse JSON object from LLM response.

    Args:
        response: Raw LLM response text

    Returns:
        Parsed dict, or empty dict if parsing fails
    """
    if not response or not response.strip():
        return {}

    # Try direct parsing first
    try:
        result = json.loads(response)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
    if code_block_match:
        try:
            result = json.loads(code_block_match.group(1))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Try finding JSON object pattern
    json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    # Try fixing common JSON issues
    cleaned = response.strip()
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)

    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    logger.warning("Failed to parse JSON object from response: %s...", response[:200])
    return {}


# Analysis prompts
METHODOLOGY_ANALYSIS = """Analyze the methodology section of this AI safety paper for errors.

Paper content:
{content}

Look for:
1. Missing details in experimental setup
2. Inconsistent procedures
3. Missing controls or baselines
4. Statistical issues
5. Reproducibility problems

Return ONLY a valid JSON array of issues found (no markdown, no explanation):
[
  {{
    "type": "methodology|statistical|reproducibility",
    "severity": "critical|major|moderate|minor",
    "location": "section/page/line",
    "description": "detailed description",
    "evidence": "specific text or finding",
    "suggestion": "how to fix"
  }}
]

If no issues found, return: []"""


CLAIM_ANALYSIS = """Analyze the claims in this AI safety paper.

Paper content:
{content}

Look for:
1. Unsupported claims
2. Overstated conclusions
3. Missing caveats
4. Logical fallacies
5. Inconsistencies between claims and evidence

Return ONLY a valid JSON array of issues found (no markdown, no explanation):
[
  {{
    "type": "claim|logical",
    "severity": "critical|major|moderate|minor",
    "location": "section/page/line",
    "description": "detailed description",
    "evidence": "specific text or finding",
    "suggestion": "how to fix"
  }}
]

If no issues found, return: []"""


EXPERIMENT_ANALYSIS = """Analyze the experiments in this AI safety paper.

Paper content:
{content}

Look for:
1. Missing baselines
2. Insufficient evaluation metrics
3. Cherry-picked results
4. Missing error bars/confidence intervals
5. Incomplete ablation studies

Return ONLY a valid JSON array of issues found (no markdown, no explanation):
[
  {{
    "type": "experimental",
    "severity": "critical|major|moderate|minor",
    "location": "section/page/line",
    "description": "detailed description",
    "evidence": "specific text or finding",
    "suggestion": "how to fix"
  }}
]

If no issues found, return: []"""


REPRODUCIBILITY_ANALYSIS = """Analyze the reproducibility of this AI safety paper.

Paper content:
{content}

Look for:
1. Missing code availability
2. Missing data availability
3. Missing hyperparameters
4. Missing random seeds
5. Missing environment details

Return ONLY a valid JSON object (no markdown, no explanation):
{{
  "score": 0.0-1.0,
  "issues": [
    {{
      "type": "reproducibility",
      "severity": "...",
      "description": "...",
      "suggestion": "..."
    }}
  ],
  "strengths": ["list of reproducibility strengths"],
  "weaknesses": ["list of reproducibility weaknesses"]
}}"""


class PaperErrorDetector:
    """Detects errors in AI safety papers using MiMo API."""
    
    def __init__(self, client: MiMoClient | None = None) -> None:
        self.client = client or MiMoClient()
        self.analyses: list[PaperAnalysis] = []
    
    def analyze_paper(
        self,
        paper_id: str,
        title: str,
        content: str,
    ) -> PaperAnalysis:
        """Analyze a paper for errors.
        
        Args:
            paper_id: Paper identifier (e.g., arxiv ID)
            title: Paper title
            content: Paper content to analyze
            
        Returns:
            PaperAnalysis with all findings
        """
        logger.info("Analyzing paper: %s", paper_id)
        
        if not content or not content.strip():
            logger.warning("Empty content provided for paper %s", paper_id)
            return PaperAnalysis(paper_id=paper_id, title=title)
        
        analysis = PaperAnalysis(paper_id=paper_id, title=title)
        
        # Truncate content if too long
        if len(content) > 10000:
            content = content[:10000] + "\n\n[truncated]"
        
        # Run different analyses
        try:
            methodology_errors = self._analyze_methodology(content)
            analysis.errors.extend(methodology_errors)
        except Exception as exc:
            logger.error("Methodology analysis failed for %s: %s", paper_id, exc)
        
        try:
            claim_errors = self._analyze_claims(content)
            analysis.errors.extend(claim_errors)
        except Exception as exc:
            logger.error("Claim analysis failed for %s: %s", paper_id, exc)
        
        try:
            experiment_errors = self._analyze_experiments(content)
            analysis.errors.extend(experiment_errors)
        except Exception as exc:
            logger.error("Experiment analysis failed for %s: %s", paper_id, exc)
        
        try:
            repro_analysis = self._analyze_reproducibility(content)
            analysis.reproducibility_score = repro_analysis.get("score", 0.5)
            analysis.strengths.extend(repro_analysis.get("strengths", []))
            analysis.weaknesses.extend(repro_analysis.get("weaknesses", []))
        except Exception as exc:
            logger.error("Reproducibility analysis failed for %s: %s", paper_id, exc)
        
        # Calculate scores
        analysis.methodology_score = self._calculate_methodology_score(analysis)
        analysis.overall_score = self._calculate_overall_score(analysis)
        
        self.analyses.append(analysis)
        return analysis
    
    def _parse_error(self, issue: dict[str, Any], default_type: ErrorType) -> PaperError | None:
        """Safely parse a single error from dict.

        Args:
            issue: Dictionary with error fields
            default_type: Default error type if not specified

        Returns:
            PaperError or None if parsing fails
        """
        try:
            error_type_str = issue.get("type", default_type.value)
            try:
                error_type = ErrorType(error_type_str)
            except ValueError:
                error_type = default_type

            severity_str = issue.get("severity", "moderate")
            try:
                severity = ErrorSeverity(severity_str)
            except ValueError:
                severity = ErrorSeverity.MODERATE

            return PaperError(
                error_type=error_type,
                severity=severity,
                location=issue.get("location", "unknown"),
                description=issue.get("description", ""),
                evidence=issue.get("evidence", ""),
                suggestion=issue.get("suggestion", ""),
                confidence=0.7,
            )
        except Exception as exc:
            logger.warning("Failed to parse error issue: %s - %s", issue, exc)
            return None
    
    def _analyze_methodology(self, content: str) -> list[PaperError]:
        """Analyze methodology for errors."""
        prompt = METHODOLOGY_ANALYSIS.format(content=content)
        response = self.client.ask_single(prompt)

        errors = []
        issues = _safe_parse_json_array(response)
        for issue in issues:
            parsed = self._parse_error(issue, ErrorType.METHODOLOGY)
            if parsed:
                errors.append(parsed)

        return errors
    
    def _analyze_claims(self, content: str) -> list[PaperError]:
        """Analyze claims for errors."""
        prompt = CLAIM_ANALYSIS.format(content=content)
        response = self.client.ask_single(prompt)

        errors = []
        issues = _safe_parse_json_array(response)
        for issue in issues:
            parsed = self._parse_error(issue, ErrorType.CLAIM)
            if parsed:
                errors.append(parsed)

        return errors
    
    def _analyze_experiments(self, content: str) -> list[PaperError]:
        """Analyze experiments for errors."""
        prompt = EXPERIMENT_ANALYSIS.format(content=content)
        response = self.client.ask_single(prompt)

        errors = []
        issues = _safe_parse_json_array(response)
        for issue in issues:
            parsed = self._parse_error(issue, ErrorType.EXPERIMENTAL)
            if parsed:
                errors.append(parsed)

        return errors
    
    def _analyze_reproducibility(self, content: str) -> dict[str, Any]:
        """Analyze reproducibility."""
        prompt = REPRODUCIBILITY_ANALYSIS.format(content=content)
        response = self.client.ask_single(prompt)

        result = _safe_parse_json_object(response)
        if not result:
            return {"score": 0.5, "strengths": [], "weaknesses": []}

        # Validate score is in range
        score = result.get("score", 0.5)
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            score = 0.5

        return {
            "score": score,
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
        }
    
    def _calculate_methodology_score(self, analysis: PaperAnalysis) -> float:
        """Calculate methodology score."""
        methodology_errors = [
            e for e in analysis.errors
            if e.error_type in (ErrorType.METHODOLOGY, ErrorType.STATISTICAL)
        ]
        
        if not methodology_errors:
            return 0.9
        
        # Deduct points for errors
        deductions = {
            ErrorSeverity.CRITICAL: 0.3,
            ErrorSeverity.MAJOR: 0.15,
            ErrorSeverity.MODERATE: 0.05,
            ErrorSeverity.MINOR: 0.02,
        }
        
        total_deduction = sum(
            deductions.get(e.severity, 0)
            for e in methodology_errors
        )
        
        return max(0.0, 1.0 - total_deduction)
    
    def _calculate_overall_score(self, analysis: PaperAnalysis) -> float:
        """Calculate overall quality score."""
        # Weighted average
        weights = {
            "methodology": 0.3,
            "reproducibility": 0.3,
            "errors": 0.4,
        }
        
        # Error score
        if not analysis.errors:
            error_score = 1.0
        else:
            critical = sum(1 for e in analysis.errors if e.severity == ErrorSeverity.CRITICAL)
            major = sum(1 for e in analysis.errors if e.severity == ErrorSeverity.MAJOR)
            error_score = max(0.0, 1.0 - (critical * 0.3 + major * 0.15))
        
        overall = (
            weights["methodology"] * analysis.methodology_score +
            weights["reproducibility"] * analysis.reproducibility_score +
            weights["errors"] * error_score
        )
        
        return round(overall, 2)
    
    def get_summary(self) -> dict[str, Any]:
        """Get summary of all analyses."""
        if not self.analyses:
            return {"status": "no_analyses"}
        
        total_papers = len(self.analyses)
        total_errors = sum(len(a.errors) for a in self.analyses)
        avg_score = sum(a.overall_score for a in self.analyses) / total_papers
        
        error_counts = {}
        for analysis in self.analyses:
            for error in analysis.errors:
                error_type = error.error_type.value
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_papers": total_papers,
            "total_errors": total_errors,
            "average_score": avg_score,
            "error_counts": error_counts,
        }
    
    def save_analysis(
        self,
        analysis: PaperAnalysis,
        output_path: Path,
    ) -> None:
        """Save analysis to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("Analysis saved to %s", output_path)
    
    def save_all_analyses(self, output_dir: Path) -> None:
        """Save all analyses."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for analysis in self.analyses:
            filename = f"analysis_{analysis.paper_id.replace(':', '_')}.json"
            output_path = output_dir / filename
            self.save_analysis(analysis, output_path)
        
        # Save summary
        summary_path = output_dir / "analysis_summary.json"
        summary_path.write_text(
            json.dumps(self.get_summary(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def create_paper_analyzer(
    client: MiMoClient | None = None,
) -> PaperErrorDetector:
    """Create paper error detector."""
    return PaperErrorDetector(client=client)
