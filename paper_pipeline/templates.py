"""Prompt templates per research section (CALLS)."""

from __future__ import annotations

from typing import Any


def _fmt(template: str, ctx: dict[str, Any]) -> str:
    return template.format(**ctx)


# Keys must match mission.sections_needed options and default Mission.sections_needed.
SECTION_PROMPTS: dict[str, str] = {
    "related_work": (
        "Search recent academic and grey literature (roughly 2020–present) on {topic}. "
        "Return: (1) a short annotated bibliography with DOI/arXiv/URL when available, "
        "(2) BibTeX entries for the most important 8–15 sources, "
        "(3) key findings per cluster of work. Be explicit about limitations of prior art."
    ),
    "sota": (
        "What is the current state of the art for {topic}? "
        "List benchmark datasets, standard metrics, reported scores or ranges, and typical architectures or paradigms. "
        "Cite sources with URLs where possible."
    ),
    "gaps": (
        "What open problems, methodological gaps, or underexplored settings exist for {topic}? "
        "Prioritize gaps that matter for a submission targeting {paper_target}. "
        "Structure as bullet points with a one-line rationale each."
    ),
    "datasets": (
        "List public datasets relevant to {topic}: name, access URL, license, approximate size, "
        "modalities, and known caveats (geography, label noise, temporal drift)."
    ),
    "methodology": (
        "Propose a concrete methodology for investigating {topic} with a path toward a paper at {paper_target}. "
        "Include: problem formulation, baselines to compare against, proposed method outline, "
        "and what would count as a minimal viable result."
    ),
    "experiments": (
        "Design an experiment plan for {topic}: suggested baselines, metrics, ablations, "
        "computational budget considerations, and a table outline (Markdown table) for results."
    ),
    "related_code": (
        "Find open-source repositories, libraries, or reference implementations related to {topic}. "
        "For each, give URL, license, last update signal if visible, and one-line relevance."
    ),
    "writing_hook": (
        "Write a compelling opening paragraph (3–6 sentences) for a paper abstract on {topic}, "
        "aimed at readers of {paper_target}. Do not invent empirical numbers; stay high-level."
    ),
    "abstract": (
        "Draft a structured abstract for {topic} for {paper_target}: Background, Gap, Method, Results (placeholder if unknown), "
        "Conclusion. Mark uncertain claims clearly."
    ),
    "conclusion": (
        "Write a concise conclusion for {topic} aimed at {paper_target}: main takeaways, "
        "what was shown vs. left open, and one paragraph on reproducibility (CPU-only, small models)."
    ),
    "limitations": (
        "List clear limitations and threats to validity for work on {topic} targeting {paper_target}: "
        "scope, synthetic vs. real data, interpretability claims, and what would require GPU or larger models."
    ),
    "discussion": (
        "Provide a discussion section for {topic} for {paper_target}: relate findings to prior work, "
        "broader impact for safety/alignment if relevant, and suggested next experiments."
    ),
}


def prompt_for_section(section: str, ctx: dict[str, Any]) -> str:
    """Build prompt for a section key."""

    template = SECTION_PROMPTS.get(section)
    if template is None:
        msg = f"Unknown section {section!r}. Known: {sorted(SECTION_PROMPTS)}"
        raise KeyError(msg)
    return _fmt(template, ctx)


QUALITY_CHECK_TEMPLATE = (
    "You are reviewing a research manuscript draft for fit with the venue: {paper_target}.\n\n"
    "Below is the full draft (possibly truncated). List concrete gaps: missing citations, weak methodology, "
    "unclear experiments, ethical/safety issues, and formatting issues for that venue.\n\n"
    "--- DRAFT ---\n{draft}\n--- END ---\n"
)

CODE_README_TEMPLATE = """# Generated experiment code (manual / agent step)

This folder is reserved for implementation aligned with:

- `../methodology.md`
- `../experiments.md`

## Suggested non-interactive workflow

1. Open this repo in Cursor.
2. Ensure project rules (`.cursorrules` in pipeline root) are loaded.
3. Run Agent once with: implement minimal runnable code under `outputs/code/` that matches the experiment table
   in `experiments.md`, using the methodology in `methodology.md`.

No automated Cursor CLI was invoked by `paper-pipeline` (portability).

Topic: **{topic}**
"""
