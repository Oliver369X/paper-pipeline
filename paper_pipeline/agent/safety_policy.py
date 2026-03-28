"""Pre/post policy checks for autonomous steps (complements SafetyController)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PolicyResult(BaseModel):
    allowed: bool
    rule_id: str
    reasons: list[str] = Field(default_factory=list)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def policy_check_pre_goal(output_dir: Path, *, selected_goal_type: str) -> PolicyResult:
    """Hard gates before scheduling a step (invalid metrics, etc.)."""
    tri = _read_json(output_dir / "triage" / "triage_report.json")
    errs = list(tri.get("metrics_validation_errors") or tri.get("metrics_bundle_strict_errors") or [])
    if errs:
        return PolicyResult(
            allowed=False,
            rule_id="invalid_metrics_block_autonomy",
            reasons=[str(e) for e in errs],
        )
    _ = selected_goal_type  # reserved for future budget / tool matrix
    return PolicyResult(allowed=True, rule_id="policy_pre_allow", reasons=[])


def policy_check_post_action(output_dir: Path, *, dry_run: bool) -> PolicyResult:
    """Lightweight post-step integrity (V1: dry-run always passes)."""
    _ = output_dir
    if dry_run:
        return PolicyResult(allowed=True, rule_id="post_action_dry_run", reasons=[])
    return PolicyResult(allowed=True, rule_id="post_action_ok", reasons=[])
