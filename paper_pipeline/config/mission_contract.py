"""Strict mission contract validation (CLI/API parity)."""

from __future__ import annotations

from typing import Any

from paper_pipeline.mission import Mission


class MissionValidationError(ValueError):
    """Raised when a mission violates the published contract."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or [message]


# Known deprecated top-level keys (inform warnings only; still accepted if mapped)
_DEPRECATED_ALIASES: dict[str, str] = {}


def normalize_mission_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Apply alias mapping and defaults before Pydantic validation."""

    out = dict(data)
    for old, new in _DEPRECATED_ALIASES.items():
        if old in out and new not in out:
            out[new] = out.pop(old)
    if "mission_version" not in out:
        out["mission_version"] = 1
    return out


def validate_mission_contract(mission: Mission) -> None:
    """Raise MissionValidationError if the mission cannot run safely.

    v2 missions enforce stricter defaults (quality path, reproducibility hints).
    """

    errors: list[str] = []
    if not (mission.topic or "").strip():
        errors.append("topic must be non-empty")
    if mission.max_perplexity_calls < 1 or mission.max_perplexity_calls > 64:
        errors.append("max_perplexity_calls must be between 1 and 64")

    if mission.mission_version >= 2:
        if not (mission.paper_target or "").strip():
            errors.append("mission_version>=2 requires non-empty paper_target")
        # Quality validation is mandatory for v2 "sane" runs
        if not mission.enable_quality_check:
            errors.append("mission_version>=2 requires enable_quality_check: true")

    if errors:
        raise MissionValidationError("Mission contract validation failed", errors=errors)
