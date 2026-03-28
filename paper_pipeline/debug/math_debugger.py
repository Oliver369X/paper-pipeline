"""Math debugging loop: classify errors, collect context, consult Perplexity, escalate."""

from __future__ import annotations

import textwrap
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from paper_pipeline.debug.debug_prompts import build_math_consultant_prompt, parse_math_consultant_response
from paper_pipeline.debug.error_classes import DebugTrace, MathDiagnosis
from paper_pipeline.debug.error_classifier import DebugContextCollector, MathErrorClassifier

if TYPE_CHECKING:
    from perplexity_webui_scraper import Perplexity


class PerplexityMathConsultant:
    """Consult Perplexity with a structured math-debugging prompt."""

    def __init__(self, client: Perplexity) -> None:
        self._client = client

    def diagnose(self, trace: DebugTrace) -> MathDiagnosis:
        from perplexity_webui_scraper import ConversationConfig

        prompt = build_math_consultant_prompt(trace)
        conv = self._client.create_conversation(
            ConversationConfig(model="best", citation_mode="markdown", language="en-US"),
        )
        conv.ask(prompt)
        raw_answer = (conv.answer or "").strip()
        return parse_math_consultant_response(raw_answer)


class MathDebuggingLoop:
    """Orchestrate Cursor retries then Perplexity escalation for math errors."""

    CURSOR_MAX_ATTEMPTS: int = 3
    PERPLEXITY_MAX_ATTEMPTS: int = 2

    def __init__(
        self,
        context_collector: DebugContextCollector,
        consultant: PerplexityMathConsultant | None = None,
        output_dir: Path | None = None,
    ) -> None:
        self._collector = context_collector
        self._consultant = consultant
        self._output_dir = output_dir or Path("outputs")
        self._failures: dict[str, list[str]] = defaultdict(list)

    def record_cursor_failure(
        self, test_name: str, stack_trace: str, fix_attempted: str
    ) -> bool:
        self._failures[test_name].append(fix_attempted)
        return len(self._failures[test_name]) >= self.CURSOR_MAX_ATTEMPTS

    def escalate_to_perplexity(
        self, test_name: str, stack_trace: str
    ) -> MathDiagnosis:
        if self._consultant is None:
            raise RuntimeError("No PerplexityMathConsultant configured for escalation")

        fixes = self._failures.get(test_name, [])
        trace = self._collector.collect(
            test_name=test_name,
            stack_trace=stack_trace,
            cursor_fixes=fixes,
            n_failures=len(fixes),
        )
        diagnosis = self._consultant.diagnose(trace)
        self._generate_human_briefing(trace, diagnosis)
        return diagnosis

    def _generate_human_briefing(
        self, trace: DebugTrace, diagnosis: MathDiagnosis
    ) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        filename = f"debug_briefing_{trace.test_name}_{ts}.md"
        path = self._output_dir / filename

        fixes_list = "\n".join(
            f"  {i+1}. {f}" for i, f in enumerate(trace.cursor_attempted_fixes)
        ) or "  (none)"
        refs_list = "\n".join(
            f"  - {r}" for r in diagnosis.paper_references
        ) or "  (none)"

        content = textwrap.dedent(f"""\
            # Debug Briefing: {trace.test_name}

            **Experiment:** {trace.exp_id}
            **Error class:** {trace.error_class.name}
            **Consecutive failures:** {trace.n_consecutive_failures}
            **Confidence:** {diagnosis.confidence}
            **Human review required:** {diagnosis.requires_human_escalation}

            ## Stack Trace

            ```
            {trace.raw_stack_trace}
            ```

            ## Cursor Attempted Fixes

            {fixes_list}

            ## Root Cause Analysis

            {diagnosis.root_cause_theory}

            ## Proposed Architectural Fix

            {diagnosis.architectural_fix}

            ## Corrected Code

            ```python
            {diagnosis.corrected_code_snippet}
            ```

            ## References

            {refs_list}
        """)

        path.write_text(content, encoding="utf-8")
        return path


__all__ = [
    "DebugContextCollector",
    "MathDebuggingLoop",
    "MathErrorClassifier",
    "PerplexityMathConsultant",
]
