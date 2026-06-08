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
    "peer_review": (
        "Simulate a structured peer review of a manuscript outline on {topic} for {paper_target}. "
        "Include: Summary, Strengths, Weaknesses, Missing citations or related work, "
        "Suggestions for improvement. Do not invent empirical numbers."
    ),
    # AI Safety specific templates
    "safety_related_work": (
        "Search recent academic literature (2020–present) on AI safety, alignment, and robustness for {topic}. "
        "Focus on: (1) jailbreak attacks and defenses, (2) red teaming methodologies, (3) alignment techniques, "
        "(4) safety benchmarks (HarmBench, ToxiGen, etc.), (5) adversarial robustness. "
        "Return annotated bibliography with DOI/arXiv/URL. Include BibTeX entries for 10–15 key papers."
    ),
    "threat_model": (
        "Define a comprehensive threat model for {topic} targeting {paper_target}. "
        "Include: (1) attacker capabilities and goals, (2) attack vectors (prompt injection, jailbreak, encoding bypass), "
        "(3) target model vulnerabilities, (4) success criteria for attacks, (5) defense assumptions. "
        "Structure as a formal threat model with adversary model and security properties."
    ),
    "attack_methodology": (
        "Propose attack methodologies for evaluating safety of {topic} at {paper_target}. "
        "Include: (1) jailbreak techniques (prefix/suffix, role-play, encoding), (2) prompt injection strategies, "
        "(3) adversarial example generation, (4) red teaming protocols, (5) metrics for attack success rate (ASR). "
        "Provide concrete attack prompts and evaluation criteria."
    ),
    "defense_mechanism": (
        "Propose defense mechanisms for {topic} targeting {paper_target}. "
        "Include: (1) safety training techniques (RLHF, DPO, constitutional AI), (2) input/output filtering, "
        "(3) guardrail architectures, (4) detection mechanisms for adversarial inputs, (5) robustness certifications. "
        "Compare trade-offs between safety and utility."
    ),
    "safety_experiments": (
        "Design safety experiments for {topic} at {paper_target}. "
        "Include: (1) benchmark selection (HarmBench, ToxiGen, BBQ, etc.), (2) attack success rate measurement, "
        "(3) refusal rate analysis, (4) alignment score calculation, (5) robustness evaluation, "
        "(6) bias and fairness assessment. Provide experiment table with metrics and baselines."
    ),
    "ethical_considerations": (
        "Analyze ethical considerations for {topic} targeting {paper_target}. "
        "Include: (1) potential harms and misuse scenarios, (2) dual-use concerns, (3) fairness and bias issues, "
        "(4) privacy implications, (5) transparency requirements, (6) responsible disclosure considerations. "
        "Provide mitigation strategies for each concern."
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

RESEARCH_PLAN_TEMPLATE = (
    "You are a research planner. Topic: {topic}\n"
    "Target: {paper_target}\n"
    "Sections: {sections}\n\n"
    "Return ONLY valid JSON with this shape:\n"
    '{{"schema_version": 1, "sections": {{"SECTION_NAME": {{"queries": ["..."], "mode": "discovery|verification|synthesis"}}}}}}\n'
    "Each section needs 1-3 queries (20-500 chars each)."
)

QUALITY_STAGE1_TEMPLATE = (
    "You are selecting sections for focused peer review.\n"
    "Topic: {topic}\n"
    "Draft excerpt (first 8000 chars):\n{draft_excerpt}\n\n"
    "Available sections: {sections}\n"
    'Return ONLY JSON: {{"sections": ["section_a", "section_b"]}} with exactly 2 section keys from the list.'
)

QUALITY_STAGE2_TEMPLATE = (
    "You are an external peer reviewer (not the author). Topic: {topic}. Venue: {paper_target}.\n"
    "Review ONLY these sections: {focus_sections}\n\n"
    "Use exactly these markdown H2 headings:\n"
    "## Strengths\n## Weaknesses\n## Missing citations\n## Suggestions\n\n"
    "--- DRAFT ---\n{draft}\n--- END ---\n"
)

QUALITY_REFUTATOR_TEMPLATE = (
    "You are a skeptical reviewer trying to refute claims in this draft.\n"
    "Topic: {topic}. List unsupported claims, missing evidence, and alternative explanations.\n\n"
    "--- DRAFT ---\n{draft}\n--- END ---\n"
)

LESSONS_LEARNED_TEMPLATE = (
    "Summarize research memory and quality gaps into lessons learned (max 1500 words).\n"
    "Topic: {topic}\n\n--- MEMORY ---\n{memory}\n--- QUALITY GAPS ---\n{quality}\n--- END ---\n"
)

SAFETY_QUALITY_CHECK_TEMPLATE = (
    "You are reviewing an AI safety research manuscript for {paper_target}.\n\n"
    "Focus on:\n"
    "1. Threat model completeness\n"
    "2. Attack methodology rigor\n"
    "3. Defense mechanism effectiveness\n"
    "4. Safety benchmark coverage\n"
    "5. Ethical considerations\n"
    "6. Reproducibility of safety evaluations\n\n"
    "Below is the full draft:\n\n"
    "--- DRAFT ---\n{draft}\n--- END ---\n\n"
    "List specific safety-related gaps and recommendations."
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
