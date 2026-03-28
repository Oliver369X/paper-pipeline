"""URLs HF / GitHub y borrador."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.experiments.replication import augment_experiment_config_from_draft
from paper_pipeline.experiments.source_urls import (
    extract_urls_from_markdown,
    parse_github_repo_spec,
    parse_hf_dataset_url,
    parse_hf_model_url,
)
from paper_pipeline.mission import ExperimentRunnerConfig


def test_parse_hf_dataset_url_with_config_query() -> None:
    ds, cfg = parse_hf_dataset_url(
        "https://huggingface.co/datasets/wikitext?config=wikitext-2-raw-v1",
    )
    assert ds == "wikitext"
    assert cfg == "wikitext-2-raw-v1"


def test_parse_hf_model_url() -> None:
    assert parse_hf_model_url("https://huggingface.co/gpt2") == "gpt2"
    assert parse_hf_model_url("https://huggingface.co/meta-llama/Llama-3.2-1B") == "meta-llama/Llama-3.2-1B"


def test_parse_github() -> None:
    assert parse_github_repo_spec("https://github.com/karpathy/nanoGPT") == ("karpathy", "nanoGPT")
    assert parse_github_repo_spec("https://github.com/foo/bar/tree/main/src") == ("foo", "bar")


def test_extract_from_markdown() -> None:
    md = """
    See dataset https://huggingface.co/datasets/glue and code https://github.com/huggingface/transformers
    """
    got = extract_urls_from_markdown(md)
    assert "glue" in (got["hf_dataset_url"] or "")
    assert "github.com" in (got["code_repo_url"] or "")


def test_augment_from_draft(tmp_path: Path) -> None:
    d = tmp_path / "draft_paper.md"
    d.write_text(
        "Data from https://huggingface.co/datasets/imdb\n"
        "Code: https://github.com/user/repo\n",
        encoding="utf-8",
    )
    cfg = ExperimentRunnerConfig(
        prefer_urls_from_draft=True,
    )
    out = augment_experiment_config_from_draft(cfg, d)
    assert out.hf_dataset_url and "imdb" in out.hf_dataset_url
    assert out.code_repo_url and "user/repo" in out.code_repo_url
