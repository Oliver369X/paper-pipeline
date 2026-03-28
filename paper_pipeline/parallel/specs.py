"""Dataclasses for parallel worktree runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorktreeConfig:
    """Tuning knobs for the parallel worktree orchestrator."""

    max_concurrent_agents: int = 5
    agent_timeout_seconds: int = 1800
    keep_breakthrough_branches: bool = True
    commit_after_each_phase: bool = True


@dataclass
class AgentRunSpec:
    """Full specification for a single experiment agent."""

    exp_id: str
    hypothesis: str
    branch_name: str = ""
    command: list[str] = field(default_factory=list)
    mission_md_content: str = ""
    tier_result: int | None = None
    error_log: str | None = None
    worktree_path: Path | None = None

    def __post_init__(self) -> None:
        if not self.branch_name:
            self.branch_name = f"exp/{self.exp_id}"
