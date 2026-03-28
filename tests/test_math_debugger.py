"""Unit tests for the math debugging loop (no Perplexity calls)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from paper_pipeline.debug.error_classes import (
    DebugTrace,
    MathDiagnosis,
    MathErrorClass,
)
from paper_pipeline.debug.debug_prompts import parse_math_consultant_response
from paper_pipeline.debug.math_debugger import (
    DebugContextCollector,
    MathDebuggingLoop,
    MathErrorClassifier,
    PerplexityMathConsultant,
)

# ---------------------------------------------------------------------------
# Fixtures: realistic PyTorch-style stack traces
# ---------------------------------------------------------------------------

NAN_TRACE = """\
Traceback (most recent call last):
  File "/workspace/train.py", line 42, in train_step
    loss = criterion(output, target)
  File "/usr/lib/python3.10/site-packages/torch/nn/modules/loss.py", line 536, in forward
    return F.cross_entropy(input, target)
RuntimeError: Loss is NaN at iteration 1024
"""

SHAPE_MISMATCH_TRACE = """\
Traceback (most recent call last):
  File "/workspace/model.py", line 87, in forward
    out = self.fc(x)
  File "/usr/lib/python3.10/site-packages/torch/nn/modules/linear.py", line 114, in forward
    return F.linear(input, self.weight, self.bias)
RuntimeError: mat1 and mat2 shapes cannot be multiplied (32x768 and 512x256)
"""

OOM_TRACE = """\
Traceback (most recent call last):
  File "/workspace/train.py", line 55, in train_epoch
    output = model(batch)
torch.cuda.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB
"""

GRADIENT_EXPLOSION_TRACE = """\
Traceback (most recent call last):
  File "/workspace/train.py", line 60, in backward_pass
    loss.backward()
RuntimeError: overflow encountered in multiply during gradient computation; loss is inf
"""

UNKNOWN_TRACE = """\
Traceback (most recent call last):
  File "/workspace/utils.py", line 10, in helper
    return do_something()
ValueError: unexpected value
"""


# ---------------------------------------------------------------------------
# MathErrorClassifier tests
# ---------------------------------------------------------------------------


class TestMathErrorClassifier:
    def test_nan_detection(self) -> None:
        assert MathErrorClassifier.classify(NAN_TRACE) == MathErrorClass.NAN_LOSS

    def test_shape_mismatch_detection(self) -> None:
        assert (
            MathErrorClassifier.classify(SHAPE_MISMATCH_TRACE)
            == MathErrorClass.TENSOR_SHAPE_MISMATCH
        )

    def test_oom_detection(self) -> None:
        assert MathErrorClassifier.classify(OOM_TRACE) == MathErrorClass.CUDA_OOM

    def test_gradient_explosion_detection(self) -> None:
        assert (
            MathErrorClassifier.classify(GRADIENT_EXPLOSION_TRACE)
            == MathErrorClass.GRADIENT_EXPLOSION
        )

    def test_unknown_fallback(self) -> None:
        assert MathErrorClassifier.classify(UNKNOWN_TRACE) == MathErrorClass.UNKNOWN

    def test_empty_trace(self) -> None:
        assert MathErrorClassifier.classify("") == MathErrorClass.UNKNOWN

    def test_vanishing_gradient(self) -> None:
        trace = "RuntimeError: vanishing gradient detected in layer 3"
        assert (
            MathErrorClassifier.classify(trace)
            == MathErrorClass.GRADIENT_VANISHING
        )

    def test_numerical_instability_exp(self) -> None:
        trace = "RuntimeWarning: overflow encountered in exp"
        assert (
            MathErrorClassifier.classify(trace)
            == MathErrorClass.NUMERICAL_INSTABILITY
        )

    def test_feature_collapse(self) -> None:
        trace = "Warning: dead features detected in SAE layer"
        assert (
            MathErrorClassifier.classify(trace)
            == MathErrorClass.FEATURE_COLLAPSE
        )

    def test_metric_inconsistency(self) -> None:
        trace = "AssertionError: accuracy > 1 after aggregation"
        assert (
            MathErrorClassifier.classify(trace)
            == MathErrorClass.METRIC_INCONSISTENCY
        )


# ---------------------------------------------------------------------------
# DebugContextCollector tests
# ---------------------------------------------------------------------------


class TestDebugContextCollector:
    def test_collect_builds_trace(self, tmp_path: Path) -> None:
        src_file = tmp_path / "model.py"
        src_file.write_text(
            "\n".join(f"line_{i} = {i}" for i in range(30)),
            encoding="utf-8",
        )
        dca = tmp_path / "domain_context.yaml"
        dca.write_text(
            "mathematical_constraints:\n  - 'L = -sum(p * log(q))'\n  - 'grad_norm < 1.0'\n",
            encoding="utf-8",
        )

        stack = f"""\
Traceback (most recent call last):
  File "{src_file}", line 15, in forward
    out = self.fc(x)
RuntimeError: size mismatch
"""
        collector = DebugContextCollector(worktree_path=tmp_path, dca_path=dca)
        trace = collector.collect(
            test_name="test_forward",
            stack_trace=stack,
            cursor_fixes=["fix1", "fix2"],
            n_failures=2,
        )

        assert isinstance(trace, DebugTrace)
        assert trace.test_name == "test_forward"
        assert trace.error_class == MathErrorClass.TENSOR_SHAPE_MISMATCH
        assert trace.n_consecutive_failures == 2
        assert "line_14" in trace.failing_function_code
        assert len(trace.relevant_dca_equations) == 2
        assert trace.cursor_attempted_fixes == ["fix1", "fix2"]

    def test_collect_missing_file(self, tmp_path: Path) -> None:
        dca = tmp_path / "domain_context.yaml"
        dca.write_text("mathematical_constraints: []\n", encoding="utf-8")

        stack = """\
Traceback (most recent call last):
  File "/nonexistent/file.py", line 5, in fn
    pass
RuntimeError: nan
"""
        collector = DebugContextCollector(worktree_path=tmp_path, dca_path=dca)
        trace = collector.collect("test_x", stack, [], 1)
        assert "not found" in trace.failing_function_code

    def test_collect_no_dca(self, tmp_path: Path) -> None:
        collector = DebugContextCollector(
            worktree_path=tmp_path,
            dca_path=tmp_path / "missing.yaml",
        )
        trace = collector.collect("test_y", "RuntimeError: nan", [], 1)
        assert trace.relevant_dca_equations == []


# ---------------------------------------------------------------------------
# MathDebuggingLoop tests
# ---------------------------------------------------------------------------


class TestMathDebuggingLoop:
    def _make_loop(self, tmp_path: Path) -> MathDebuggingLoop:
        collector = DebugContextCollector(
            worktree_path=tmp_path,
            dca_path=tmp_path / "dca.yaml",
        )
        return MathDebuggingLoop(
            context_collector=collector,
            consultant=None,
            output_dir=tmp_path / "outputs",
        )

    def test_escalation_after_three_failures(self, tmp_path: Path) -> None:
        loop = self._make_loop(tmp_path)
        assert not loop.record_cursor_failure("test_a", "trace", "fix_1")
        assert not loop.record_cursor_failure("test_a", "trace", "fix_2")
        assert loop.record_cursor_failure("test_a", "trace", "fix_3")

    def test_no_escalation_before_threshold(self, tmp_path: Path) -> None:
        loop = self._make_loop(tmp_path)
        assert not loop.record_cursor_failure("test_b", "trace", "fix_1")
        assert not loop.record_cursor_failure("test_b", "trace", "fix_2")

    def test_separate_test_names_tracked_independently(self, tmp_path: Path) -> None:
        loop = self._make_loop(tmp_path)
        loop.record_cursor_failure("test_x", "trace", "fix_1")
        loop.record_cursor_failure("test_x", "trace", "fix_2")
        assert not loop.record_cursor_failure("test_y", "trace", "fix_1")
        assert loop.record_cursor_failure("test_x", "trace", "fix_3")

    def test_escalate_without_consultant_raises(self, tmp_path: Path) -> None:
        loop = self._make_loop(tmp_path)
        with pytest.raises(RuntimeError, match="No PerplexityMathConsultant"):
            loop.escalate_to_perplexity("test_z", NAN_TRACE)

    def test_human_briefing_writes_file(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "briefings"
        collector = DebugContextCollector(
            worktree_path=tmp_path,
            dca_path=tmp_path / "dca.yaml",
        )
        loop = MathDebuggingLoop(
            context_collector=collector,
            consultant=None,
            output_dir=output_dir,
        )

        trace = DebugTrace(
            exp_id="debug-test",
            error_class=MathErrorClass.NAN_LOSS,
            raw_stack_trace=NAN_TRACE,
            failing_function_code="loss = criterion(output, target)",
            relevant_dca_equations=["L = -sum(p * log(q))"],
            cursor_attempted_fixes=["added eps to log", "clamped output"],
            test_name="test_nan",
            n_consecutive_failures=3,
        )
        diagnosis = MathDiagnosis(
            root_cause_theory="Log of zero in cross-entropy",
            architectural_fix="Clamp logits before log_softmax",
            corrected_code_snippet="output = torch.clamp(output, min=1e-7)",
            paper_references=["arxiv:2103.00020"],
            confidence="medium",
            requires_human_escalation=False,
        )

        path = loop._generate_human_briefing(trace, diagnosis)

        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "test_nan" in content
        assert "NAN_LOSS" in content
        assert "Log of zero" in content
        assert "arxiv:2103.00020" in content
        assert "torch.clamp" in content


# ---------------------------------------------------------------------------
# parse_math_consultant_response (unit, no network)
# ---------------------------------------------------------------------------


class TestPerplexityMathConsultantParsing:
    def test_parse_with_code_and_refs(self) -> None:
        raw = """\
The root cause is numerical instability in the softmax layer.

The fix is to use log-softmax instead of separate log and softmax.

```python
output = F.log_softmax(logits, dim=-1)
```

References: arxiv:2103.00020, (Vaswani et al., 2017)
"""
        diag = parse_math_consultant_response(raw)
        assert diag.corrected_code_snippet == "output = F.log_softmax(logits, dim=-1)"
        assert len(diag.paper_references) >= 1
        assert diag.confidence in ("medium", "high")
        assert not diag.requires_human_escalation

    def test_parse_no_code_no_refs(self) -> None:
        raw = "I am not sure what is wrong."
        diag = parse_math_consultant_response(raw)
        assert diag.corrected_code_snippet == ""
        assert diag.paper_references == []
        assert diag.confidence == "low"

    def test_parse_requires_human(self) -> None:
        raw = "This is complex. REQUIRES_HUMAN_REVIEW."
        diag = parse_math_consultant_response(raw)
        assert diag.requires_human_escalation is True
