"""Mission contract validation."""

from __future__ import annotations

import pytest

from paper_pipeline.config.mission_contract import MissionValidationError, validate_mission_contract
from paper_pipeline.mission import Mission


def test_validate_v1_minimal_ok() -> None:
    m = Mission(mission_version=1, topic="T", paper_target="V")
    validate_mission_contract(m)


def test_validate_v2_requires_quality() -> None:
    m = Mission(
        mission_version=2,
        topic="T",
        paper_target="Venue",
        enable_quality_check=False,
    )
    with pytest.raises(MissionValidationError):
        validate_mission_contract(m)


def test_validate_v2_ok() -> None:
    m = Mission(
        mission_version=2,
        topic="T",
        paper_target="Venue",
        enable_quality_check=True,
    )
    validate_mission_contract(m)
