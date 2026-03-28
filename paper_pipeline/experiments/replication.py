"""Combinar URLs explícitas en la misión con enlaces detectados en el borrador."""

from __future__ import annotations

import logging
from pathlib import Path

from paper_pipeline.experiments.source_urls import extract_urls_from_markdown
from paper_pipeline.mission import ExperimentRunnerConfig

logger = logging.getLogger(__name__)


def augment_experiment_config_from_draft(
    cfg: ExperimentRunnerConfig,
    draft_path: Path | None,
) -> ExperimentRunnerConfig:
    """Si ``prefer_urls_from_draft`` y existe ``draft_paper.md``, rellena URLs vacías."""

    if not cfg.prefer_urls_from_draft or draft_path is None or not draft_path.is_file():
        return cfg
    try:
        text = draft_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.warning("No se pudo leer borrador para URLs: %s", exc)
        return cfg
    ext = extract_urls_from_markdown(text)
    updates: dict[str, object] = {}
    if not (cfg.hf_dataset_url or "").strip() and ext.get("hf_dataset_url"):
        updates["hf_dataset_url"] = ext["hf_dataset_url"]
    if not (cfg.code_repo_url or "").strip() and ext.get("code_repo_url"):
        updates["code_repo_url"] = ext["code_repo_url"]
    if not updates:
        return cfg
    logger.info("URLs tomadas del borrador: %s", updates)
    return cfg.model_copy(update=updates)
