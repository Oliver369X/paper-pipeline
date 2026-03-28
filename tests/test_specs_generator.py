"""Specs generator from mission hypotheses."""

from __future__ import annotations

from paper_pipeline.mission import Hypothesis, Mission
from paper_pipeline.parallel.specs_generator import specs_from_mission


def test_specs_empty_without_hypotheses() -> None:
    m = Mission(mission_version=1, topic="T", paper_target="P")
    assert specs_from_mission(m) == []


def test_specs_from_hypotheses() -> None:
    m = Mission(
        mission_version=1,
        topic="T",
        paper_target="P",
        hypotheses=[Hypothesis(id="h1", description="test hyp")],
    )
    specs = specs_from_mission(m)
    assert len(specs) == 1
    assert specs[0]["exp_id"] == "h1"
