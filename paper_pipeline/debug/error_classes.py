"""Math-oriented error taxonomy and structures for debug escalation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

# Signal for runners when Cursor debug attempts are exhausted
ESCALATE_TO_PERPLEXITY_SIGNAL = "__ESCALATE_TO_PERPLEXITY__"


class MathErrorClass(Enum):
    """Categories of ML/math failures for specialized diagnostics."""

    NAN_LOSS = auto()
    GRADIENT_EXPLOSION = auto()
    GRADIENT_VANISHING = auto()
    TENSOR_SHAPE_MISMATCH = auto()
    FEATURE_COLLAPSE = auto()
    NUMERICAL_INSTABILITY = auto()
    CONVERGENCE_FAILURE = auto()
    METRIC_INCONSISTENCY = auto()
    CUDA_OOM = auto()
    UNKNOWN = auto()


# Short prompt fragments used when building Perplexity consultant prompts
_DIAGNOSTIC_FRAGMENTS: dict[MathErrorClass, str] = {
    MathErrorClass.NAN_LOSS: """
TASK: Diagnose NaN loss mathematically (log(0), inf-inf, overflow in exp).
Cite the paper section that defines stable numerics for this objective.
""",
    MathErrorClass.GRADIENT_EXPLOSION: """
TASK: Diagnose gradient explosion — which layer norm explodes, clipping threshold,
learning rate compatibility, cite reference.
""",
    MathErrorClass.GRADIENT_VANISHING: """
TASK: Diagnose vanishing gradients — depth, activation, residual paths, cite reference.
""",
    MathErrorClass.TENSOR_SHAPE_MISMATCH: """
TASK: Diagnose tensor shapes — expected dims per paper, correct einsum/reshape.
""",
    MathErrorClass.FEATURE_COLLAPSE: """
TASK: Diagnose feature collapse / dead features (e.g. SAE) — L1 schedule, init, cite.
""",
    MathErrorClass.NUMERICAL_INSTABILITY: """
TASK: Diagnose numerical instability — softmax/log domain, mixed precision, epsilon.
""",
    MathErrorClass.CONVERGENCE_FAILURE: """
TASK: Diagnose non-convergence — optimizer, schedule, data normalization.
""",
    MathErrorClass.METRIC_INCONSISTENCY: """
TASK: Diagnose invalid metrics — probabilities outside [0,1], wrong aggregation.
""",
    MathErrorClass.CUDA_OOM: """
TASK: GPU OOM — batch size, gradient checkpointing, activation memory, cite common fixes.
""",
    MathErrorClass.UNKNOWN: """
TASK: Identify mathematical root cause and architecturally correct fix; cite papers.
""",
}


def diagnostic_prompt_fragment_for_class(error_class: MathErrorClass) -> str:
    """Return non-empty diagnostic fragment for every enum member."""
    return _DIAGNOSTIC_FRAGMENTS[error_class].strip()


@dataclass
class DebugTrace:
    """Bundle sent to Perplexity math consultant."""

    exp_id: str
    error_class: MathErrorClass
    raw_stack_trace: str
    failing_function_code: str
    relevant_dca_equations: list[str]
    cursor_attempted_fixes: list[str]
    test_name: str
    n_consecutive_failures: int


@dataclass
class MathDiagnosis:
    """Parsed response from external consultant."""

    root_cause_theory: str
    architectural_fix: str
    corrected_code_snippet: str
    paper_references: list[str] = field(default_factory=list)
    confidence: str = "low"  # "high", "medium", "low"
    requires_human_escalation: bool = False
