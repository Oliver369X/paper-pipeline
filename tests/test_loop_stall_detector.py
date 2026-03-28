"""Loop stall detector."""

from __future__ import annotations

from paper_pipeline.validation.loop_stall_detector import is_stalled


def test_stalled_identical() -> None:
    assert is_stalled("hello", "hello") is True


def test_not_stalled_substantial_change() -> None:
    assert is_stalled("a" * 100, "b" * 100) is False
