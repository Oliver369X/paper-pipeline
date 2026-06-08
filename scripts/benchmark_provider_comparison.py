"""Benchmark provider comparison (Perplexity vs Mistral)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from paper_pipeline.mission import load_mission
from paper_pipeline.validators import validate_draft, validate_section

_CITATION_RE = re.compile(r"\[[\d,\s]+\]|https?://|arxiv:\s*\d{4}\.\d{4,5}", re.IGNORECASE)
_H2_H3 = re.compile(r"^#{2,3}\s+", re.MULTILINE)


def _read_run_state_errors(out: Path) -> list[Any]:
    p = out / "run_state.json"
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        errs = data.get("errors")
        return errs if isinstance(errs, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def compute_metrics(out: Path, mission_sections: list[str]) -> dict[str, Any]:
    section_files = [out / f"{s}.md" for s in mission_sections]
    passed = 0
    total = 0
    total_chars = 0
    for sf in section_files:
        if not sf.is_file():
            continue
        total += 1
        text = sf.read_text(encoding="utf-8")
        total_chars += len(text)
        if validate_section(text, min_chars=50).ok:
            passed += 1

    draft_path = out / "draft_paper.md"
    draft_ok = False
    citation_markers = 0
    if draft_path.is_file():
        draft = draft_path.read_text(encoding="utf-8")
        draft_ok = validate_draft(draft, expected_sections=mission_sections).ok
        citation_markers = len(_CITATION_RE.findall(draft))

    quality_path = out / "quality_gaps.md"
    quality_headings = 0
    if quality_path.is_file():
        quality_headings = len(_H2_H3.findall(quality_path.read_text(encoding="utf-8")))

    ledger_path = out / "run_ledger.json"
    wall_time_sec: float | None = None
    if ledger_path.is_file():
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            started = ledger.get("started_at")
            finished = ledger.get("finished_at")
            if started and finished:
                from datetime import datetime

                t0 = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(str(finished).replace("Z", "+00:00"))
                wall_time_sec = (t1 - t0).total_seconds()
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            pass

    calls_used = 0
    state_path = out / "run_state.json"
    if state_path.is_file():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            steps = st.get("completed_steps")
            if isinstance(steps, list):
                calls_used = sum(
                    1
                    for s in steps
                    if isinstance(s, str)
                    and (
                        s.startswith("perplexity:")
                        or s.startswith("mistral:")
                        or s.startswith("mimo:")
                        or s == "step:quality_check"
                        or s == "step:research_plan"
                    )
                )
        except (OSError, json.JSONDecodeError):
            pass

    ratio = (passed / total) if total else 0.0
    return {
        "sections_pass_validate": {"passed": passed, "total": total, "ratio": round(ratio, 3)},
        "draft_pass_validate": draft_ok,
        "total_chars": total_chars,
        "citation_markers": citation_markers,
        "quality_gaps_sections": quality_headings,
        "wall_time_sec": wall_time_sec,
        "llm_calls": calls_used,
        "errors": _read_run_state_errors(out),
    }


def _write_mission_variant(base: Path, provider: str, output_dir: Path) -> Path:
    text = base.read_text(encoding="utf-8")
    lines = text.splitlines()
    out_lines: list[str] = []
    in_fm = False
    fm_done = False
    for line in lines:
        if line.strip() == "---" and not fm_done:
            if not in_fm:
                in_fm = True
                out_lines.append(line)
                continue
            out_lines.append(f"output_dir: {output_dir.as_posix()}")
            out_lines.append(line)
            in_fm = False
            fm_done = True
            continue
        if in_fm:
            if line.startswith("provider:"):
                out_lines.append(f"provider: {provider}")
            elif line.startswith("output_dir:"):
                continue
            elif line.startswith("enable_cursor_cli:"):
                out_lines.append("enable_cursor_cli: false")
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)
    tmp = base.parent / f"mission_{provider}.md"
    tmp.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return tmp


def run_pipeline_subprocess(mission_path: Path, cwd: Path) -> int:
    cmd = [sys.executable, "-m", "paper_pipeline", str(mission_path)]
    proc = subprocess.run(cmd, cwd=str(cwd), check=False)
    return int(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Perplexity vs Mistral providers")
    parser.add_argument(
        "--mission",
        type=Path,
        default=Path("data/missions/repo-adoption-mistral/mission.md"),
    )
    parser.add_argument(
        "--benchmark-root",
        type=Path,
        default=Path("outputs/benchmark"),
    )
    parser.add_argument("--skip-perplexity", action="store_true")
    parser.add_argument("--skip-mistral", action="store_true")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    mission_path = (repo_root / args.mission).resolve()
    mission = load_mission(mission_path)
    bench_root = (repo_root / args.benchmark_root).resolve()
    bench_root.mkdir(parents=True, exist_ok=True)

    results: dict[str, Any] = {
        "schema_version": 1,
        "mission": str(mission_path),
        "providers": {},
        "disclaimer": (
            "Mistral sections do not use live web search. Metrics are objective heuristics, "
            "not scientific truth scores."
        ),
    }

    for provider, skip in (("perplexity", args.skip_perplexity), ("mistral", args.skip_mistral)):
        if skip:
            continue
        out_dir = bench_root / provider
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        variant = _write_mission_variant(mission_path, provider, Path(f"outputs/benchmark/{provider}"))
        t0 = time.monotonic()
        code = run_pipeline_subprocess(variant, repo_root)
        elapsed = round(time.monotonic() - t0, 2)
        metrics = compute_metrics(out_dir, mission.sections_needed)
        if metrics.get("wall_time_sec") is None:
            metrics["wall_time_sec"] = elapsed
        metrics["exit_code"] = code
        results["providers"][provider] = metrics

    report_json = bench_root / "comparison_report.json"
    report_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Provider comparison report",
        "",
        results["disclaimer"],
        "",
        "| Metric | Perplexity | Mistral |",
        "|--------|------------|---------|",
    ]
    keys = [
        "sections_pass_validate",
        "draft_pass_validate",
        "total_chars",
        "citation_markers",
        "quality_gaps_sections",
        "wall_time_sec",
        "llm_calls",
        "errors",
    ]
    for key in keys:
        p_val = results["providers"].get("perplexity", {}).get(key, "—")
        m_val = results["providers"].get("mistral", {}).get(key, "—")
        lines.append(f"| {key} | {p_val} | {m_val} |")

    (bench_root / "comparison_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {report_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
