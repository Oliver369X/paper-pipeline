"""Classify math/ML errors and collect debug context from stack traces."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from paper_pipeline.debug.error_classes import DebugTrace, MathErrorClass

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


class MathErrorClassifier:
    """Case-insensitive substring classifier for ML/math stack traces."""

    _PATTERNS: list[tuple[MathErrorClass, list[str]]] = [
        (MathErrorClass.NAN_LOSS, ["nan", "loss is nan", "loss became nan"]),
        (
            MathErrorClass.GRADIENT_EXPLOSION,
            [
                "exploding gradient",
                "overflow encountered in multiply",
                "inf in gradient",
                "loss is inf",
            ],
        ),
        (MathErrorClass.GRADIENT_VANISHING, ["vanishing gradient", "grad is zero"]),
        (
            MathErrorClass.TENSOR_SHAPE_MISMATCH,
            [
                "size mismatch",
                "shape mismatch",
                "mat1 and mat2 shapes cannot be multiplied",
            ],
        ),
        (MathErrorClass.FEATURE_COLLAPSE, ["dead features", "feature collapse", "no active features"]),
        (
            MathErrorClass.NUMERICAL_INSTABILITY,
            [
                "overflow encountered in exp",
                "divide by zero",
                "log of zero",
                "underflow",
            ],
        ),
        (MathErrorClass.CUDA_OOM, ["cuda out of memory", "oom", "out of memory"]),
        (MathErrorClass.METRIC_INCONSISTENCY, ["accuracy > 1", "probabilities do not sum"]),
    ]

    @classmethod
    def classify(cls, stack_trace: str) -> MathErrorClass:
        lower = stack_trace.lower()
        for error_class, patterns in cls._PATTERNS:
            for pat in patterns:
                if pat in lower:
                    return error_class
        return MathErrorClass.UNKNOWN


_FILE_LINE_RE = re.compile(r'File "([^"]+)", line (\d+)')


class DebugContextCollector:
    """Gather surrounding code and DCA equations for a failing test."""

    def __init__(self, worktree_path: Path, dca_path: Path) -> None:
        self._worktree = worktree_path
        self._dca_path = dca_path

    def collect(
        self,
        test_name: str,
        stack_trace: str,
        cursor_fixes: list[str],
        n_failures: int,
    ) -> DebugTrace:
        error_class = MathErrorClassifier.classify(stack_trace)
        func_code = self._extract_failing_function_code(stack_trace)
        equations = self._extract_dca_equations()

        return DebugTrace(
            exp_id=f"debug-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
            error_class=error_class,
            raw_stack_trace=stack_trace,
            failing_function_code=func_code,
            relevant_dca_equations=equations,
            cursor_attempted_fixes=list(cursor_fixes),
            test_name=test_name,
            n_consecutive_failures=n_failures,
        )

    def _extract_failing_function_code(self, stack_trace: str) -> str:
        matches = list(_FILE_LINE_RE.finditer(stack_trace))
        if not matches:
            return ""
        last = matches[-1]
        filepath = Path(last.group(1))
        lineno = int(last.group(2))

        if not filepath.is_absolute():
            filepath = self._worktree / filepath

        if not filepath.exists():
            return f"# file not found: {filepath}"

        try:
            lines = filepath.read_text(encoding="utf-8").splitlines()
        except OSError:
            return f"# could not read: {filepath}"

        start = max(0, lineno - 11)
        end = min(len(lines), lineno + 10)
        return "\n".join(lines[start:end])

    def _extract_dca_equations(self) -> list[str]:
        if yaml is None:
            return ["# pyyaml not installed"]
        if not self._dca_path.exists():
            return []
        try:
            data = yaml.safe_load(self._dca_path.read_text(encoding="utf-8"))
        except Exception:
            return ["# failed to parse DCA"]
        if not isinstance(data, dict):
            return []
        constraints = data.get("mathematical_constraints")
        if isinstance(constraints, list):
            return [str(c) for c in constraints]
        return []
