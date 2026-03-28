"""Perplexity query templates and DCA text parsers."""

from __future__ import annotations

import re

from paper_pipeline.epistemic.models import (
    ComputeRequirements,
    KnownPitfall,
    PoisonPill,
    ReferenceImplementation,
)

QUERY_SOTA = (
    "What are the top 15-20 most cited and influential research papers from 2024-2026 "
    "about '{topic}'? For each paper list: title, authors, year, key technical finding, "
    "and the main mathematical contribution. Target venue level: {venue}."
)

QUERY_PITFALLS = (
    "What are the most common implementation mistakes and failure modes when coding "
    "'{topic}' in Python / PyTorch? For each pitfall give: the error symptom "
    "(e.g. 'loss becomes NaN'), the root cause, and the verified fix. "
    "Cite specific papers or GitHub issues where possible."
)

QUERY_REPOS = (
    "What are the top 5-8 most-used open source GitHub repositories for '{topic}'? "
    "For each repo list: name, GitHub URL, star count, key architectural decisions "
    "that make it state-of-the-art, and any known anti-patterns or technical debt."
)

QUERY_COMPUTE = (
    "What are the typical GPU memory and training time requirements for a standard "
    "'{topic}' experiment? Give answers in GB and minutes. "
    "What GPU is most commonly used in recent papers (T4, A100, H100, etc.)? "
    "Is it feasible on a free Google Colab T4 instance?"
)


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://[^\s\)\]>\"']+", text)


def extract_bullet_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^(?:[-*]|\d+[.\)])\s+(.+)", stripped)
        if match:
            items.append(match.group(1).strip())
    return items


def extract_github_urls(text: str) -> list[str]:
    return [u for u in extract_urls(text) if "github.com" in u]


def parse_float(text: str, pattern: str, default: float) -> float:
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except (ValueError, IndexError):
            pass
    return default


def parse_pitfalls(raw: str) -> list[KnownPitfall]:
    items = extract_bullet_items(raw)
    if not items:
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
        items = paragraphs[:10]

    pitfalls: list[KnownPitfall] = []
    for item in items:
        symptom = ""
        fix = ""
        source = ""
        sym_match = re.search(r"(?:symptom|error|problem|issue)[:\s]+(.+?)(?:\.|$)", item, re.I)
        if sym_match:
            symptom = sym_match.group(1).strip()
        fix_match = re.search(r"(?:fix|solution|workaround|resolve)[:\s]+(.+?)(?:\.|$)", item, re.I)
        if fix_match:
            fix = fix_match.group(1).strip()
        src_match = re.search(r"\(([^)]*(?:et al|20\d{2})[^)]*)\)", item)
        if src_match:
            source = src_match.group(1).strip()
        pitfalls.append(
            KnownPitfall(
                description=item,
                source_paper=source,
                symptom=symptom,
                fix=fix,
            ),
        )
    return pitfalls


def parse_repos(raw: str) -> list[ReferenceImplementation]:
    gh_urls = extract_github_urls(raw)
    items = extract_bullet_items(raw)

    repos: list[ReferenceImplementation] = []
    seen_urls: set[str] = set()
    for url in gh_urls:
        clean = url.rstrip("/.,;:)")
        if clean in seen_urls:
            continue
        seen_urls.add(clean)
        parts = clean.rstrip("/").split("/")
        name = "/".join(parts[-2:]) if len(parts) >= 2 else clean
        decisions: list[str] = []
        for item in items:
            if name.split("/")[-1].lower() in item.lower():
                decisions.append(item)
        repos.append(
            ReferenceImplementation(
                name=name,
                github_url=clean,
                key_design_decisions=decisions[:5],
                what_not_to_copy=[],
            ),
        )

    if not repos and items:
        for item in items[:5]:
            repos.append(
                ReferenceImplementation(
                    name=item[:60],
                    github_url="",
                    key_design_decisions=[item],
                    what_not_to_copy=[],
                ),
            )
    return repos


def parse_compute(raw: str) -> ComputeRequirements:
    gpu_gb = parse_float(raw, r"(\d+(?:\.\d+)?)\s*(?:GB|gb)", 8.0)
    minutes = parse_float(raw, r"(\d+(?:\.\d+)?)\s*(?:minutes|mins|min)", 30.0)

    requires_gpu = bool(re.search(r"(?:GPU|CUDA|gpu|cuda)", raw))
    delegate = gpu_gb > 12.0

    accel = "T4"
    accel_match = re.search(r"\b(T4|A100|H100|L4|V100|A10G)\b", raw)
    if accel_match:
        accel = accel_match.group(1)

    return ComputeRequirements(
        estimated_gpu_memory_gb=gpu_gb,
        estimated_training_time_minutes=minutes,
        requires_gpu=requires_gpu,
        delegate_to_colab=delegate,
        colab_accelerator=accel,
    )


def generate_poison_pills(topic: str) -> list[PoisonPill]:
    return [
        PoisonPill(
            false_claim=(f"The standard evaluation metric for '{topic}' is pixel accuracy."),
            reason_it_is_false=(
                "Pixel accuracy is a segmentation metric unrelated to most ML research topics."
            ),
            detection_query=(f"Is pixel accuracy the standard evaluation metric for {topic}?"),
        ),
        PoisonPill(
            false_claim=(
                f"The Transformer architecture used in '{topic}' was invented by Yann LeCun in 1998."
            ),
            reason_it_is_false=(
                "The Transformer was introduced by Vaswani et al. in 2017 ('Attention Is All You Need')."
            ),
            detection_query=("Who invented the Transformer architecture and in what year?"),
        ),
        PoisonPill(
            false_claim=(
                f"Standard practice in '{topic}' is to use a learning rate greater than 1.0."
            ),
            reason_it_is_false=(
                "Learning rates > 1.0 destabilise training; typical range is 1e-5 to 1e-2."
            ),
            detection_query=(f"Is a learning rate greater than 1.0 standard practice in {topic}?"),
        ),
    ]
