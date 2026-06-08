"""Export a small appendix bundle for preprint / supplementary material (no secrets)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _package_version() -> str:
    try:
        return version("paper-pipeline")
    except PackageNotFoundError:
        return "unknown"


def _git_head(repo_root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        out = (proc.stdout or "").strip()
        return out if proc.returncode == 0 and out else "unknown"
    except OSError:
        return "unknown"


def _write_pytest_collect(repo_root: Path, dest: Path) -> None:
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        parts = [proc.stdout or ""]
        if proc.stderr:
            parts.append("\n--- stderr ---\n")
            parts.append(proc.stderr)
        if proc.returncode != 0:
            parts.append(f"\n--- exit {proc.returncode} ---\n")
        dest.write_text("".join(parts), encoding="utf-8")
    except OSError as exc:
        dest.write_text(f"pytest_collect_failed: {exc}\n", encoding="utf-8")


def export_appendix_bundle(
    *,
    out_dir: Path,
    repo_root: Path,
    case_study_outputs: Path | None = None,
) -> None:
    """Write VERSION, git_commit, agent_eval JSON, pytest collect, case_study_trace, benchmark bundle."""

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "VERSION").write_text(_package_version() + "\n", encoding="utf-8")
    (out_dir / "git_commit.txt").write_text(_git_head(repo_root) + "\n", encoding="utf-8")

    from paper_pipeline.agent_eval.eval_metrics import scorecard_to_stable_dict
    from paper_pipeline.agent_eval.eval_runner import run_all
    from paper_pipeline.reporting.benchmark_bundle import (
        benchmark_bundle_to_markdown_table,
        build_benchmark_bundle,
    )

    with tempfile.TemporaryDirectory() as td:
        report = run_all(Path(td))
    payload = scorecard_to_stable_dict(report)
    (out_dir / "agent_eval_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    _write_pytest_collect(repo_root, out_dir / "pytest_collect.txt")

    from paper_pipeline.reporting.case_study_trace import (
        build_case_study_trace,
        build_minimal_safety_usecase_trace,
    )

    cs_out = case_study_outputs
    if cs_out is None:
        default_mission = repo_root / "data" / "missions" / "4f6715a65f4c" / "outputs"
        if default_mission.is_dir() and (default_mission / "run_ledger.json").is_file():
            trace = build_case_study_trace(default_mission)
        else:
            trace = build_minimal_safety_usecase_trace(repo_root)
    else:
        trace = build_case_study_trace(cs_out.resolve())

    (out_dir / "case_study_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    bundle = build_benchmark_bundle(
        repo_root=repo_root,
        case_study_outputs=cs_out,
        agent_eval_report_payload=payload,
    )
    (out_dir / "benchmark_bundle.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "benchmark_table.md").write_text(
        benchmark_bundle_to_markdown_table(bundle),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write preprint appendix files (version, git, agent_eval, pytest collect, traces, benchmark bundle).",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        required=True,
        help="Output directory (created if missing).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root for git and pytest (default: current working directory).",
    )
    parser.add_argument(
        "--case-study-outputs",
        type=Path,
        default=None,
        metavar="OUTPUTS_DIR",
        help="Mission outputs/ directory for case_study_trace.json (default: bundled mission or P2 fixture).",
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or Path.cwd()).resolve()
    export_appendix_bundle(
        out_dir=args.out.resolve(),
        repo_root=repo_root,
        case_study_outputs=args.case_study_outputs,
    )
    print(f"Wrote appendix bundle under {args.out.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
