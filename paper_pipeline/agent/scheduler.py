"""Single autonomous step orchestration (dry-run by default; no live Perplexity here)."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from paper_pipeline.agent.goals import ensure_goals_seed
from paper_pipeline.agent.goal_selection import build_goal_selection_from_output_dir
from paper_pipeline.agent.safety import SafetyContext, SafetyController
from paper_pipeline.agent.safety_policy import policy_check_post_action, policy_check_pre_goal

AGENT_DECISIONS_NAME = "agent_decisions.jsonl"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def build_safety_context_for_agent_step(output_dir: Path) -> SafetyContext:
    """Build safety context from on-disk artifacts (same signals as other flows)."""
    obj = _read_json(output_dir / "objective_state.json")
    gates = dict(obj.get("gates") or {})
    loop_reasons: list[str] = []
    if gates.get("loop_stopped"):
        loop_reasons.append("loop_stopped")
    tri = _read_json(output_dir / "triage" / "triage_report.json")
    metrics_errs = list(
        tri.get("metrics_validation_errors") or tri.get("metrics_bundle_strict_errors") or []
    )
    pub = _read_json(output_dir / "publication" / "publish_decision.json")
    blockers = list(pub.get("blocking_reasons") or [])
    tier = tri.get("tier")
    triage_tier = int(tier) if isinstance(tier, int) else None
    eligible = bool(pub.get("eligible_for_publication", False))
    return SafetyContext(
        candidate_action="agent_step",
        triage_tier=triage_tier,
        eligible_for_publication=eligible,
        loop_stop_reasons=loop_reasons,
        metrics_validation_errors=[str(x) for x in metrics_errs],
        publish_blocking_reasons=[str(x) for x in blockers],
        source_artifacts=[
            "objective_state.json",
            "triage/triage_report.json",
            "publication/publish_decision.json",
        ],
    )


def append_agent_decision(output_dir: Path, record: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / AGENT_DECISIONS_NAME
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return path


def run_agent_step(
    output_dir: Path,
    mission: Any | None = None,
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """One planning step: goals seed → selection → safety + policy → append decision JSONL.

    **Does not** run ``paper-pipeline`` unless ``PAPER_PIPELINE_AUTONOMY_EXECUTE`` is set **and**
    ``dry_run`` is false **and** ``mission.mode == \"autonomy\"`` — and even then execution is
    intentionally a no-op until explicitly wired (records ``note`` in the decision).
    """
    from paper_pipeline.mission import Mission

    ensure_goals_seed(output_dir)
    selection = build_goal_selection_from_output_dir(output_dir)
    ctx = build_safety_context_for_agent_step(output_dir)
    safety = SafetyController().evaluate(ctx)
    pre = policy_check_pre_goal(output_dir, selected_goal_type=selection.selected_goal_type)
    post = policy_check_post_action(output_dir, dry_run=dry_run)

    mode = "standard"
    if mission is not None and isinstance(mission, Mission):
        mode = mission.mode

    execute_env = os.environ.get("PAPER_PIPELINE_AUTONOMY_EXECUTE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    would_execute = (
        not dry_run
        and execute_env
        and mission is not None
        and isinstance(mission, Mission)
        and mission.mode == "autonomy"
        and safety.decision == "ALLOW"
        and pre.allowed
        and post.allowed
    )

    record: dict[str, Any] = {
        "ts": datetime.now(UTC).isoformat(),
        "dry_run": dry_run,
        "mission_mode": mode,
        "selected_goal_type": selection.selected_goal_type,
        "goal_text": selection.goal_text,
        "safety": safety.model_dump(mode="python"),
        "policy_pre": pre.model_dump(mode="python"),
        "policy_post": post.model_dump(mode="python"),
        "would_execute": would_execute,
    }
    if would_execute:
        record["note"] = (
            "PAPER_PIPELINE_AUTONOMY_EXECUTE is set and gates passed; "
            "pipeline invocation is not wired in this build (intentional no-op)."
        )

    append_agent_decision(output_dir, record)
    return {
        "ok": True,
        "output_dir": str(output_dir.resolve()),
        "decision_path": str((output_dir / AGENT_DECISIONS_NAME).resolve()),
        "record": record,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one autonomous agent step (dry-run default).")
    parser.set_defaults(dry_run=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Mission outputs directory (e.g. data/missions/<id>/outputs)",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="dry_run",
        action="store_false",
        help="Set dry_run=false (still requires autonomy mission + PAPER_PIPELINE_AUTONOMY_EXECUTE for would_execute)",
    )
    args = parser.parse_args()
    dry = args.dry_run
    mission = None
    mission_path = args.output_dir.parent / "mission.md"
    if mission_path.is_file():
        from paper_pipeline.mission import load_mission

        try:
            mission = load_mission(mission_path)
        except (OSError, ValueError):
            mission = None
    out = run_agent_step(args.output_dir, mission, dry_run=dry)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
