"""Build ``outputs/evidence/`` index and copy references."""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from paper_pipeline.mission import Mission


def build_evidence_bundle(output_dir: Path, mission: Mission) -> Path:
    """Write ``evidence_index.json`` and ensure key artifacts are listed."""

    ev = output_dir / "evidence"
    ev.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, list[str]] = {
        "draft": ["draft_paper.md"] if (output_dir / "draft_paper.md").is_file() else [],
        "sections": [f"{s}.md" for s in mission.sections_needed if (output_dir / f"{s}.md").is_file()],
        "metrics": ["metrics.json"] if (output_dir / "metrics.json").is_file() else [],
        "triage": ["triage/triage_report.json"] if (output_dir / "triage" / "triage_report.json").is_file() else [],
        "validation": ["validation/quality_validation.json"]
        if (output_dir / "validation" / "quality_validation.json").is_file()
        else [],
        "claims": ["evidence/claims.json"] if (ev / "claims.json").is_file() else [],
    }

    index: dict[str, Any] = {
        "schema_version": 1,
        "mission_version": mission.mission_version,
        "artifacts": artifacts,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    p = ev / "evidence_index.json"
    p.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p
