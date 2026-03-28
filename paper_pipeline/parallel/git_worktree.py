"""Git worktree lifecycle and serialized commits."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from paper_pipeline.parallel.specs import AgentRunSpec

logger = logging.getLogger(__name__)


class GitWorktreeManager:
    """Low-level helper that creates, removes, and commits inside worktrees."""

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path
        self._commit_queue: asyncio.Queue[
            tuple[Path, str, str, asyncio.Event]
        ] = asyncio.Queue()
        self._commit_worker_task: Optional[asyncio.Task[None]] = None

    def start_commit_worker(self) -> None:
        self._commit_worker_task = asyncio.create_task(
            self._commit_worker_loop(),
        )
        logger.info("Commit worker started (serialised queue).")

    async def stop_commit_worker(self) -> None:
        if self._commit_worker_task is not None:
            self._commit_worker_task.cancel()
            try:
                await self._commit_worker_task
            except asyncio.CancelledError:
                pass
            self._commit_worker_task = None

    async def _commit_worker_loop(self) -> None:
        while True:
            worktree_path, branch, message, done_event = (
                await self._commit_queue.get()
            )
            try:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=str(worktree_path),
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", message, "--allow-empty"],
                    cwd=str(worktree_path),
                    check=True,
                    capture_output=True,
                )
                logger.info("[%s] Commit: %s", branch, message)
            except subprocess.CalledProcessError as exc:
                logger.error(
                    "[%s] Commit failed: %s",
                    branch,
                    exc.stderr.decode(errors="replace"),
                )
            finally:
                done_event.set()
                self._commit_queue.task_done()

    async def commit_async(
        self, worktree_path: Path, branch: str, message: str
    ) -> None:
        done_event = asyncio.Event()
        await self._commit_queue.put(
            (worktree_path, branch, message, done_event),
        )
        await done_event.wait()

    async def create_worktree(self, spec: AgentRunSpec) -> Path:
        worktree_path = self.repo_path.parent / f"wt_{spec.exp_id}"

        if worktree_path.exists():
            logger.warning(
                "[%s] Stale worktree found, removing...", spec.exp_id
            )
            await self.remove_worktree(spec)

        default_branch = self._detect_default_branch()

        try:
            subprocess.run(
                [
                    "git", "worktree", "add",
                    "-b", spec.branch_name,
                    str(worktree_path),
                    default_branch,
                ],
                cwd=str(self.repo_path),
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"Failed to create worktree for {spec.exp_id}: "
                f"{exc.stderr.decode(errors='replace')}",
            ) from exc

        logger.info("[%s] Worktree created at %s", spec.exp_id, worktree_path)
        return worktree_path

    def _detect_default_branch(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
        )
        branch = result.stdout.strip()
        return branch if branch else "main"

    async def remove_worktree(
        self, spec: AgentRunSpec, keep_branch: bool = False
    ) -> None:
        worktree_path = self.repo_path.parent / f"wt_{spec.exp_id}"

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=str(self.repo_path),
            capture_output=True,
        )

        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)

        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=str(self.repo_path),
            capture_output=True,
        )

        if not keep_branch:
            subprocess.run(
                ["git", "branch", "-D", spec.branch_name],
                cwd=str(self.repo_path),
                capture_output=True,
            )
            logger.info(
                "[%s] Worktree and branch removed.", spec.exp_id
            )
        else:
            logger.info(
                "[%s] Worktree removed; branch preserved.", spec.exp_id
            )

    def inject_mission(
        self, spec: AgentRunSpec, worktree_path: Path
    ) -> None:
        mission_path = worktree_path / "mission.md"
        mission_path.write_text(
            spec.mission_md_content, encoding="utf-8",
        )
