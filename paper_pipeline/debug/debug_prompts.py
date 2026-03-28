"""Prompts and parsing for Perplexity math consultant."""

from __future__ import annotations

import re
import textwrap

from paper_pipeline.debug.error_classes import DebugTrace, MathDiagnosis, diagnostic_prompt_fragment_for_class

_CODE_BLOCK_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
_PAPER_REF_RE = re.compile(
    r"(?:"
    r"(?:arxiv[:\s]*\d{4}\.\d{4,5})"
    r"|(?:https?://arxiv\.org/abs/\d{4}\.\d{4,5})"
    r"|(?:\([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?,?\s*\d{4}\))"
    r")",
    re.IGNORECASE,
)


def build_math_consultant_prompt(trace: DebugTrace) -> str:
    fragment = diagnostic_prompt_fragment_for_class(trace.error_class)
    equations_block = "\n".join(trace.relevant_dca_equations) or "(none)"
    fixes_block = "\n".join(f"  - {f}" for f in trace.cursor_attempted_fixes) or "(none)"

    return textwrap.dedent(f"""\
        You are a mathematical ML debugging consultant.

        {fragment}

        ERROR CLASS: {trace.error_class.name}
        TEST: {trace.test_name}
        CONSECUTIVE FAILURES: {trace.n_consecutive_failures}

        STACK TRACE:
        {trace.raw_stack_trace}

        FAILING CODE:
        ```python
        {trace.failing_function_code}
        ```

        DOMAIN EQUATIONS:
        {equations_block}

        CURSOR ATTEMPTED FIXES:
        {fixes_block}

        INSTRUCTIONS:
        1. State the mathematical root cause in one paragraph.
        2. Propose an architecturally correct fix with a code snippet (```python ... ```).
        3. Cite relevant papers (arxiv IDs or author-year).
        4. If you are not confident, say REQUIRES_HUMAN_REVIEW.
    """)


def parse_math_consultant_response(raw: str) -> MathDiagnosis:
    code_blocks = _CODE_BLOCK_RE.findall(raw)
    corrected_code = code_blocks[0].strip() if code_blocks else ""

    references = _PAPER_REF_RE.findall(raw)

    paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
    root_cause = paragraphs[0] if paragraphs else raw
    architectural_fix = paragraphs[1] if len(paragraphs) > 1 else root_cause

    if len(references) >= 3:
        confidence = "high"
    elif len(references) >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    requires_human = "REQUIRES_HUMAN_REVIEW" in raw.upper()

    return MathDiagnosis(
        root_cause_theory=root_cause,
        architectural_fix=architectural_fix,
        corrected_code_snippet=corrected_code,
        paper_references=references,
        confidence=confidence,
        requires_human_escalation=requires_human,
    )
