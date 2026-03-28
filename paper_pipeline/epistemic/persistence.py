"""Persist Domain Context Artifact to YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from paper_pipeline.epistemic.models import DomainContextArtifact, dca_to_yaml_dict


def save_domain_context_yaml(dca: DomainContextArtifact, output_dir: Path) -> Path:
    """Write ``domain_context.yaml`` under *output_dir*."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "domain_context.yaml"
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            dca_to_yaml_dict(dca),
            fh,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
    return path
