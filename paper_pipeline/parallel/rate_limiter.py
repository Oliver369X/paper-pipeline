"""Rate limiter with exponential backoff and jitter for API calls."""

from __future__ import annotations

import asyncio
import logging
import random
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


@dataclass
class RateLimiterConfig:
    """Configuration for the exponential-backoff rate limiter.

    Attributes:
        max_retries: Maximum number of retry attempts before giving up.
        initial_backoff_seconds: Base wait time for the first retry.
        max_backoff_seconds: Upper bound on the computed wait time.
        jitter_factor: Fraction of randomness applied to each wait
            (e.g. 0.3 means the wait is multiplied by a value in
            [1 - 0.3, 1 + 0.3]).
    """

    max_retries: int = 5
    initial_backoff_seconds: float = 2.0
    max_backoff_seconds: float = 120.0
    jitter_factor: float = 0.3


class APIRateLimiter:
    """Retries coroutines that fail with rate-limit errors.

    Uses exponential backoff with jitter so that concurrent callers
    do not all retry at the same instant ("thundering herd").

    Example wait sequence (initial=2, jitter=0.3):
        attempt 0: 2s  * uniform(0.7, 1.3)
        attempt 1: 4s  * uniform(0.7, 1.3)
        attempt 2: 8s  * uniform(0.7, 1.3)
        attempt 3: 16s * uniform(0.7, 1.3)
        attempt 4: 32s * uniform(0.7, 1.3)
    """

    def __init__(self, config: RateLimiterConfig | None = None) -> None:
        self.config = config or RateLimiterConfig()

    def compute_wait_time(self, attempt: int) -> float:
        """Return the backoff duration for the given 0-indexed attempt."""
        base = min(
            self.config.initial_backoff_seconds * (2 ** attempt),
            self.config.max_backoff_seconds,
        )
        jitter = 1.0 + random.uniform(
            -self.config.jitter_factor,
            self.config.jitter_factor,
        )
        return base * jitter

    async def execute_with_retry(
        self,
        label: str,
        coro_factory: Callable[[], Awaitable[Any]],
        is_rate_limit_error: Callable[[Exception], bool],
    ) -> Any:
        """Execute *coro_factory()* with automatic retries on rate-limit errors.

        Args:
            label: Human-readable identifier used in log messages.
            coro_factory: Zero-argument callable that returns a **new**
                awaitable on each invocation (coroutines are single-use).
            is_rate_limit_error: Predicate that returns ``True`` when the
                caught exception represents a rate-limit (HTTP 429, quota
                exceeded, etc.).

        Returns:
            Whatever the awaitable produced by *coro_factory* returns.

        Raises:
            RuntimeError: If all retries are exhausted.
            Exception: Re-raised immediately when *is_rate_limit_error*
                returns ``False``.
        """
        last_exc: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                return await coro_factory()
            except Exception as exc:
                if not is_rate_limit_error(exc):
                    raise
                last_exc = exc
                wait = self.compute_wait_time(attempt)
                logger.warning(
                    "[%s] Rate-limit hit (attempt %d/%d). "
                    "Waiting %.1fs before retry...",
                    label,
                    attempt + 1,
                    self.config.max_retries,
                    wait,
                )
                await asyncio.sleep(wait)

        raise RuntimeError(
            f"[{label}] Max retries ({self.config.max_retries}) exhausted "
            f"for rate-limited operation. Last error: {last_exc}"
        )
