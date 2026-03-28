"""Parallel experiment orchestrator using Git worktrees."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from paper_pipeline.parallel.agent_executor import run_single_agent_in_worktree
from paper_pipeline.parallel.git_worktree import GitWorktreeManager
from paper_pipeline.parallel.specs import AgentRunSpec, WorktreeConfig
from paper_pipeline.parallel.rate_limiter import APIRateLimiter, RateLimiterConfig

logger = logging.getLogger(__name__)

__all__ = ["AgentRunSpec", "ParallelWorktreeOrchestrator", "WorktreeConfig"]


class ParallelWorktreeOrchestrator:
    """Launch experiment agents in parallel, each in its own Git worktree."""

    def __init__(
        self,
        repo_path: Path,
        config: WorktreeConfig | None = None,
        rate_limiter_config: RateLimiterConfig | None = None,
    ) -> None:
        self.repo_path = repo_path
        self.config = config or WorktreeConfig()
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_agents)
        self.git_manager = GitWorktreeManager(repo_path)
        self.rate_limiter = APIRateLimiter(rate_limiter_config)

    async def run_single_agent(self, spec: AgentRunSpec) -> AgentRunSpec:
        """Execute one agent inside an isolated worktree."""
        async with self.semaphore:
            return await run_single_agent_in_worktree(
                spec,
                git_manager=self.git_manager,
                agent_timeout_seconds=self.config.agent_timeout_seconds,
                commit_after_each_phase=self.config.commit_after_each_phase,
                keep_breakthrough_branches=self.config.keep_breakthrough_branches,
            )

    async def run_batch(
        self, experiments: list[AgentRunSpec],
    ) -> list[AgentRunSpec]:
        self.git_manager.start_commit_worker()
        try:
            logger.info(
                "Starting batch of %d experiments (max concurrent: %d).",
                len(experiments),
                self.config.max_concurrent_agents,
            )
            tasks = [self.run_single_agent(spec) for spec in experiments]
            results: list[AgentRunSpec] = await asyncio.gather(*tasks)
            logger.info("Batch complete (%d experiments).", len(results))
            return results
        finally:
            await self.git_manager.stop_commit_worker()
