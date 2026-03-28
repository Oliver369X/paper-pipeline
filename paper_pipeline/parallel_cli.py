"""CLI: parallel worktree batch and standalone triage (Hypervisor).

Commands:
  paper-parallel triage --mission PATH --output-dir PATH [--metrics PATH]
  paper-parallel batch --repo PATH --specs PATH
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _cmd_triage(args: argparse.Namespace) -> int:
    from paper_pipeline.mission import load_mission
    from paper_pipeline.hypervisor.triage import run_triage_for_mission
    from paper_pipeline.ledger.writer import merge_ledger_after_triage
    from paper_pipeline.publication.publish_manager import write_publish_decision

    mission = load_mission(Path(args.mission))
    out = Path(args.output_dir)
    mpath = Path(args.metrics) if args.metrics else None
    rep = run_triage_for_mission(mission, out, metrics_path=mpath)
    if rep is None:
        print("No metrics file found; nothing to triage.", file=sys.stderr)
        return 2
    write_publish_decision(out, mission)
    merge_ledger_after_triage(out)
    print(json.dumps({"tier": rep.tier, "label": rep.label, "reason": rep.reason}, indent=2))
    return 0


def _load_specs(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("specs JSON must be an array")
    return data


def _cmd_batch(args: argparse.Namespace) -> int:
    from paper_pipeline.parallel.worktree_runner import (
        AgentRunSpec,
        ParallelWorktreeOrchestrator,
        WorktreeConfig,
    )

    repo = Path(args.repo).resolve()
    raw_specs = _load_specs(Path(args.specs))
    specs: list[AgentRunSpec] = []
    for item in raw_specs:
        specs.append(
            AgentRunSpec(
                exp_id=item["exp_id"],
                hypothesis=item.get("hypothesis", ""),
                branch_name=item.get("branch_name", ""),
                command=item.get("command", []),
                mission_md_content=item.get("mission_md_content", ""),
            )
        )

    cfg = WorktreeConfig(
        max_concurrent_agents=args.max_concurrent,
        agent_timeout_seconds=args.timeout,
        keep_breakthrough_branches=not args.no_keep_breakthrough,
        commit_after_each_phase=not args.no_commit,
    )
    orch = ParallelWorktreeOrchestrator(repo, config=cfg)

    async def _run() -> list[AgentRunSpec]:
        return await orch.run_batch(specs)

    results = asyncio.run(_run())
    summary = {
        "total": len(results),
        "ok": sum(1 for s in results if not s.error_log),
        "failed": sum(1 for s in results if s.error_log),
        "experiments": [
            {"exp_id": s.exp_id, "tier": s.tier_result, "error": s.error_log} for s in results
        ],
    }
    out_summary = repo / "outputs" / "batch_summary.json"
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lb = repo / "outputs" / "leaderboard.json"
    ranked = sorted(
        (x for x in summary["experiments"] if x.get("tier") is not None),
        key=lambda x: (x.get("tier") is None, -(x.get("tier") or 0)),
    )
    lb.write_text(json.dumps({"ranked": ranked}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary["experiments"], indent=2))
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Paper-pipeline parallel / triage tools")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("triage", help="Run hypervisor triage on outputs/metrics.json")
    t.add_argument("--mission", type=Path, required=True, help="Path to mission.md")
    t.add_argument("--output-dir", type=Path, required=True, help="Pipeline output dir (e.g. outputs/)")
    t.add_argument("--metrics", type=Path, default=None, help="Override path to metrics.json")

    b = sub.add_parser("batch", help="Run a batch of worktree experiments from JSON specs")
    b.add_argument("--repo", type=Path, required=True, help="Git repository root")
    b.add_argument("--specs", type=Path, required=True, help="JSON array of AgentRunSpec fields")
    b.add_argument("--max-concurrent", type=int, default=5)
    b.add_argument("--timeout", type=int, default=1800, help="Per-agent timeout seconds")
    b.add_argument(
        "--no-keep-breakthrough",
        action="store_true",
        help="Remove branches even for tier-3 runs",
    )
    b.add_argument("--no-commit", action="store_true", help="Skip git commit after each agent")

    args = parser.parse_args()
    if args.command == "triage":
        sys.exit(_cmd_triage(args))
    if args.command == "batch":
        sys.exit(_cmd_batch(args))
    sys.exit(2)


if __name__ == "__main__":
    main()
