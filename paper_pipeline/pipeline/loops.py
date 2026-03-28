"""Single-section Perplexity and draft rebuild (used by integrated loop)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

from perplexity_webui_scraper import ConversationConfig, Perplexity

from paper_pipeline.mission import Mission
from paper_pipeline.templates import prompt_for_section

from .common import build_conversation_config

logger = logging.getLogger(__name__)

_SKIP_DRAFT_NAMES = frozenset(
    {
        "draft_paper.md",
        "quality_gaps.md",
        "cursor_turn.md",
        "next_instruction.md",
        "meta_loop_log.md",
    },
)


def run_one_perplexity_section(
    mission: Mission,
    section: str,
    out: Path,
    *,
    client: Perplexity,
    extra_prompt: str = "",
) -> Path:
    """One section write (used by integrated loop). Does not update draft; caller may call rebuild_draft_from_outputs."""

    ctx = {"topic": mission.topic, "paper_target": mission.paper_target}
    prompt = prompt_for_section(section, ctx)
    if extra_prompt.strip():
        prompt = prompt + "\n\n---\n\n" + extra_prompt.strip()
    cfg = build_conversation_config(mission)
    conversation = client.create_conversation(cfg)
    logger.info("Perplexity ask (loop): section=%s", section)
    conversation.ask(prompt)
    answer = conversation.answer or ""
    _uid = getattr(conversation, "uuid", None)
    if _uid:
        logger.info(
            "Perplexity thread backend_uuid=%s (session token account; check Library on perplexity.ai)",
            _uid,
        )
    target = out / f"{section}.md"
    header = (
        f"<!-- section={section} generated={datetime.now(UTC).isoformat()} "
        f"model={mission.model} source=loop -->\n\n"
    )
    target.write_text(header + answer + "\n", encoding="utf-8")
    return target


def rebuild_draft_from_outputs(out: Path, mission: Mission) -> None:
    """Rebuild draft_paper.md from section files in output_dir (non-linear / after loop sections)."""

    draft_parts: list[str] = [
        f"# Draft: {mission.topic}",
        "",
        f"**Target venue:** {mission.paper_target}",
        "",
        f"_Generated {datetime.now(UTC).isoformat()} UTC_",
        "",
    ]
    seen_names: set[str] = set()
    for sec in mission.sections_needed:
        p = out / f"{sec}.md"
        if p.is_file():
            draft_parts.append(f"## {sec}\n")
            draft_parts.append(p.read_text(encoding="utf-8"))
            draft_parts.append("\n")
            seen_names.add(p.name)
    for p in sorted(out.glob("*.md")):
        if p.name in _SKIP_DRAFT_NAMES or p.name in seen_names:
            continue
        draft_parts.append(f"## {p.stem}\n")
        draft_parts.append(p.read_text(encoding="utf-8"))
        draft_parts.append("\n")
    (out / "draft_paper.md").write_text("\n".join(draft_parts), encoding="utf-8")
