"""Tests for the parallel execution layer (rate limiter + worktree runner)."""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import pytest

from paper_pipeline.parallel.git_worktree import GitWorktreeManager
from paper_pipeline.parallel.rate_limiter import APIRateLimiter, RateLimiterConfig
from paper_pipeline.parallel.specs import AgentRunSpec, WorktreeConfig
from paper_pipeline.parallel.worktree_runner import ParallelWorktreeOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_git_repo(path: Path) -> None:
    """Initialise a minimal Git repo with one commit so worktrees can branch."""
    subprocess.run(
        ["git", "init"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    readme = path / "README.md"
    readme.write_text("# test repo\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "-A"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=str(path),
        check=True,
        capture_output=True,
    )


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Return a temporary directory that is a valid Git repository."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    return repo


# ---------------------------------------------------------------------------
# Rate-limiter tests
# ---------------------------------------------------------------------------

class TestRateLimiterBackoff:
    def test_backoff_increases(self) -> None:
        """Wait times must grow exponentially (ignoring jitter)."""
        cfg = RateLimiterConfig(
            initial_backoff_seconds=1.0,
            max_backoff_seconds=1000.0,
            jitter_factor=0.0,
        )
        limiter = APIRateLimiter(cfg)

        times = [limiter.compute_wait_time(i) for i in range(5)]
        for i in range(1, len(times)):
            assert times[i] > times[i - 1], (
                f"attempt {i} ({times[i]:.2f}) should exceed "
                f"attempt {i-1} ({times[i-1]:.2f})"
            )

    def test_backoff_respects_ceiling(self) -> None:
        cfg = RateLimiterConfig(
            initial_backoff_seconds=2.0,
            max_backoff_seconds=10.0,
            jitter_factor=0.0,
        )
        limiter = APIRateLimiter(cfg)
        assert limiter.compute_wait_time(100) == pytest.approx(10.0)

    def test_jitter_varies(self) -> None:
        """With jitter enabled, repeated calls for the same attempt
        should produce different values."""
        cfg = RateLimiterConfig(jitter_factor=0.3)
        limiter = APIRateLimiter(cfg)
        values = {limiter.compute_wait_time(0) for _ in range(50)}
        assert len(values) > 1, "Jitter should make wait times non-deterministic"


class TestRateLimiterRetry:
    @pytest.mark.asyncio
    async def test_succeeds_on_first_try(self) -> None:
        limiter = APIRateLimiter(RateLimiterConfig(max_retries=3))
        result = await limiter.execute_with_retry(
            "ok",
            coro_factory=lambda: asyncio.coroutine(lambda: 42)()
            if sys.version_info < (3, 11)
            else _async_value(42),
            is_rate_limit_error=lambda _: True,
        )
        assert result == 42

    @pytest.mark.asyncio
    async def test_retries_then_succeeds(self) -> None:
        cfg = RateLimiterConfig(
            max_retries=5,
            initial_backoff_seconds=0.01,
            jitter_factor=0.0,
        )
        limiter = APIRateLimiter(cfg)
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("429 Too Many Requests")
            return "done"

        result = await limiter.execute_with_retry(
            "flaky",
            coro_factory=flaky,
            is_rate_limit_error=lambda e: "429" in str(e),
        )
        assert result == "done"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_exhausts_retries(self) -> None:
        cfg = RateLimiterConfig(
            max_retries=2,
            initial_backoff_seconds=0.01,
            jitter_factor=0.0,
        )
        limiter = APIRateLimiter(cfg)

        async def always_fail() -> None:
            raise RuntimeError("rate limit exceeded")

        with pytest.raises(RuntimeError, match="Max retries"):
            await limiter.execute_with_retry(
                "fail",
                coro_factory=always_fail,
                is_rate_limit_error=lambda _: True,
            )

    @pytest.mark.asyncio
    async def test_non_rate_limit_error_propagates(self) -> None:
        limiter = APIRateLimiter()

        async def bad() -> None:
            raise ValueError("not a rate limit")

        with pytest.raises(ValueError, match="not a rate limit"):
            await limiter.execute_with_retry(
                "bad",
                coro_factory=bad,
                is_rate_limit_error=lambda _: False,
            )


# ---------------------------------------------------------------------------
# Worktree tests
# ---------------------------------------------------------------------------

class TestWorktreeCreateAndCleanup:
    @pytest.mark.asyncio
    async def test_create_and_remove(self, git_repo: Path) -> None:
        mgr = GitWorktreeManager(git_repo)
        spec = AgentRunSpec(exp_id="w1", hypothesis="test create")

        wt = await mgr.create_worktree(spec)
        assert wt.exists()
        assert (wt / "README.md").exists()

        await mgr.remove_worktree(spec)
        assert not wt.exists()

    @pytest.mark.asyncio
    async def test_stale_worktree_is_cleaned(self, git_repo: Path) -> None:
        mgr = GitWorktreeManager(git_repo)
        spec = AgentRunSpec(exp_id="stale", hypothesis="stale test")

        wt1 = await mgr.create_worktree(spec)
        assert wt1.exists()

        spec2 = AgentRunSpec(exp_id="stale", hypothesis="stale test 2")
        wt2 = await mgr.create_worktree(spec2)
        assert wt2.exists()

        await mgr.remove_worktree(spec2)


class TestCommitSerialisation:
    @pytest.mark.asyncio
    async def test_concurrent_commits_no_lock_errors(
        self, git_repo: Path
    ) -> None:
        """Three worktrees committing concurrently must not produce
        index.lock errors thanks to the serialised commit worker."""
        mgr = GitWorktreeManager(git_repo)
        mgr.start_commit_worker()

        specs = [
            AgentRunSpec(exp_id=f"c{i}", hypothesis=f"commit test {i}")
            for i in range(3)
        ]
        worktrees: list[Path] = []
        for spec in specs:
            wt = await mgr.create_worktree(spec)
            (wt / "output.txt").write_text(
                f"result-{spec.exp_id}", encoding="utf-8"
            )
            worktrees.append(wt)

        await asyncio.gather(
            *(
                mgr.commit_async(wt, spec.branch_name, f"commit {spec.exp_id}")
                for wt, spec in zip(worktrees, specs)
            )
        )

        for spec in specs:
            log = subprocess.run(
                ["git", "log", "--oneline", spec.branch_name],
                cwd=str(git_repo),
                capture_output=True,
                text=True,
            )
            assert f"commit {spec.exp_id}" in log.stdout

        for spec in specs:
            await mgr.remove_worktree(spec)

        await mgr.stop_commit_worker()


class TestInjectMission:
    @pytest.mark.asyncio
    async def test_mission_file_written(self, git_repo: Path) -> None:
        mgr = GitWorktreeManager(git_repo)
        spec = AgentRunSpec(
            exp_id="m1",
            hypothesis="mission test",
            mission_md_content="# Experiment\nHello world",
        )
        wt = await mgr.create_worktree(spec)
        mgr.inject_mission(spec, wt)

        mission = wt / "mission.md"
        assert mission.exists()
        assert mission.read_text(encoding="utf-8") == "# Experiment\nHello world"

        await mgr.remove_worktree(spec)


class TestRunBatch:
    @pytest.mark.asyncio
    async def test_batch_with_echo_commands(self, git_repo: Path) -> None:
        """Run three agents with simple echo commands; all must complete
        without errors."""
        config = WorktreeConfig(
            max_concurrent_agents=3,
            agent_timeout_seconds=30,
            commit_after_each_phase=True,
        )
        orch = ParallelWorktreeOrchestrator(git_repo, config=config)

        cmd = [sys.executable, "-c", "print('hello')"]

        specs = [
            AgentRunSpec(
                exp_id=f"echo-{i}",
                hypothesis=f"echo test {i}",
                command=cmd,
                mission_md_content=f"# Echo {i}\nRun echo.",
            )
            for i in range(3)
        ]

        results = await orch.run_batch(specs)

        assert len(results) == 3
        for r in results:
            assert r.error_log is None, f"{r.exp_id} failed: {r.error_log}"

    @pytest.mark.asyncio
    async def test_batch_ten_parallel_echo(self, git_repo: Path) -> None:
        """Ten concurrent agents (max_concurrent=10); validates parallel layer at scale."""
        config = WorktreeConfig(
            max_concurrent_agents=10,
            agent_timeout_seconds=60,
            commit_after_each_phase=True,
        )
        orch = ParallelWorktreeOrchestrator(git_repo, config=config)

        mission_yaml = (
            "---\n"
            "topic: parallel\n"
            "paper_target: test\n"
            "enable_hypervisor_triage: false\n"
            "---\n"
        )
        cmd = [sys.executable, "-c", "print(1)"]
        specs = [
            AgentRunSpec(
                exp_id=f"p{i:02d}",
                hypothesis=f"parallel scale {i}",
                command=cmd,
                mission_md_content=mission_yaml,
            )
            for i in range(10)
        ]

        results = await orch.run_batch(specs)

        assert len(results) == 10
        for r in results:
            assert r.error_log is None, f"{r.exp_id} failed: {r.error_log}"


# ---------------------------------------------------------------------------
# Async helper
# ---------------------------------------------------------------------------

async def _async_value(val: object) -> object:
    return val
