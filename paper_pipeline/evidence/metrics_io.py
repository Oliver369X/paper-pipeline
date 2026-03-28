"""Load and validate ``outputs/metrics.json`` against ``MetricsBundle``.

Triaje puede usar ``PAPER_PIPELINE_RELAX_METRICS`` para un segundo parse permisivo
(``TriageMetrics``) si el estricto falla; véase ``hypervisor/triage.py``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from paper_pipeline.evidence.metrics_model import MetricsBundle

logger = logging.getLogger(__name__)


def load_and_validate_metrics(path: Path) -> tuple[MetricsBundle | None, list[str]]:
    """Parse ``metrics.json`` and validate with Pydantic.

    Legacy JSON without ``schema_version`` is accepted: missing key defaults to ``1``
    (same as :class:`MetricsBundle`).

    Returns ``(None, errors)`` on missing file, JSON errors, or validation failure.
    """
    if not path.is_file():
        return None, []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"metrics.json read error: {exc}"]

    if not isinstance(raw, dict):
        return None, ["metrics.json must be a JSON object"]

    data: dict[str, Any] = dict(raw)
    if "schema_version" not in data:
        data["schema_version"] = 1

    try:
        bundle = MetricsBundle.model_validate(data)
    except ValidationError as exc:
        errs = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
        return None, errs

    return bundle, []
