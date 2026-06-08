"""Deep Research Bench lite — fixed questions, deterministic scoring helpers."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FIXED_QUESTIONS: list[dict[str, str]] = [
    {"id": "q1", "question": "What is retrieval-augmented generation for scientific literature?"},
    {"id": "q2", "question": "Name two benchmarks for deep research agents."},
    {"id": "q3", "question": "What is a common failure mode of LLM-generated citations?"},
    {"id": "q4", "question": "How do multi-agent research pipelines reduce hallucinations?"},
    {"id": "q5", "question": "What artifacts improve auditability in AI-assisted research?"},
]

_CITATION_RE = re.compile(r"\[[\d,\s]+\]|https?://|arxiv", re.IGNORECASE)


def score_draft_against_questions(draft_text: str) -> dict[str, Any]:
    text_lower = draft_text.lower()
    per_q: list[dict[str, Any]] = []
    for q in FIXED_QUESTIONS:
        keywords = [w for w in q["question"].lower().split() if len(w) > 4][:3]
        hits = sum(1 for kw in keywords if kw in text_lower)
        per_q.append({"id": q["id"], "keyword_hits": hits, "max_keywords": len(keywords)})
    citation_markers = len(_CITATION_RE.findall(draft_text))
    claim_lines = sum(1 for line in draft_text.splitlines() if line.strip().startswith("- "))
    return {
        "schema_version": 1,
        "questions": FIXED_QUESTIONS,
        "per_question": per_q,
        "citation_markers": citation_markers,
        "claim_bullet_lines": claim_lines,
    }


def run_benchmark(output_dir: Path, draft_path: Path | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    draft = draft_path or (output_dir / "draft_paper.md")
    if draft.is_file():
        text = draft.read_text(encoding="utf-8")
    else:
        text = " ".join(q["question"] for q in FIXED_QUESTIONS)
    report = score_draft_against_questions(text)
    out_path = output_dir / "drb_lite.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep Research Bench lite (fixed questions)")
    parser.add_argument("--out", type=Path, default=Path("outputs/benchmark"))
    parser.add_argument("--draft", type=Path, default=None)
    args = parser.parse_args()
    run_benchmark(args.out, args.draft)


if __name__ == "__main__":
    main()
