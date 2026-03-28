"""Tests for the ProveIt audit notebook generator."""

from __future__ import annotations

import nbformat

from paper_pipeline.audit.prove_it import (
    ExperimentMetadata,
    MAKEFILE_TEMPLATE,
    ProveItNotebookGenerator,
    generate_full_audit_package,
)


def _sample_metadata(*, colab: bool = True) -> ExperimentMetadata:
    return ExperimentMetadata(
        exp_id="exp_001",
        topic="Sentiment Analysis with Transformers",
        model_artifact_path="models/sentiment_v2.pt",
        test_data_path="data/test_sentiment.csv",
        target_metric="accuracy",
        claimed_metric_value=0.92,
        sota_baseline=0.89,
        model_weights_in_colab=colab,
        colab_notebook_url="https://colab.research.google.com/drive/abc123" if colab else None,
    )


def test_notebook_is_valid_ipynb(tmp_path) -> None:
    """Generated notebook must pass nbformat.validate without errors."""
    gen = ProveItNotebookGenerator(tmp_path)
    path = gen.generate(_sample_metadata(colab=True))

    nb = nbformat.read(str(path), as_version=4)
    nbformat.validate(nb)


def test_notebook_has_expected_sections(tmp_path) -> None:
    """With colab=True the notebook should have 9 cells (all sections)."""
    gen = ProveItNotebookGenerator(tmp_path)
    path = gen.generate(_sample_metadata(colab=True))

    nb = nbformat.read(str(path), as_version=4)
    assert len(nb.cells) == 9

    markdown_cells = [c for c in nb.cells if c.cell_type == "markdown"]
    code_cells = [c for c in nb.cells if c.cell_type == "code"]

    assert len(markdown_cells) == 3
    assert len(code_cells) == 6


def test_notebook_without_colab_skips_download_cell(tmp_path) -> None:
    """Without colab weights the download cell is omitted (8 cells)."""
    gen = ProveItNotebookGenerator(tmp_path)
    path = gen.generate(_sample_metadata(colab=False))

    nb = nbformat.read(str(path), as_version=4)
    assert len(nb.cells) == 8

    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    assert len(code_cells) == 5

    sources = "\n".join(c.source for c in nb.cells)
    assert "COLAB" not in sources


def test_makefile_has_required_targets(tmp_path) -> None:
    """Makefile must contain all four required targets."""
    result = generate_full_audit_package(_sample_metadata(), tmp_path)
    makefile_text = result["makefile"].read_text(encoding="utf-8")

    for target in ("verify_results", "setup", "clean", "publish_results"):
        assert f"{target}:" in makefile_text or f"{target}" in makefile_text


def test_full_audit_package_returns_paths(tmp_path) -> None:
    """generate_full_audit_package must return dict with notebook and makefile keys."""
    result = generate_full_audit_package(_sample_metadata(), tmp_path)

    assert "notebook" in result
    assert "makefile" in result
    assert result["notebook"].exists()
    assert result["makefile"].exists()
    assert result["notebook"].suffix == ".ipynb"
    assert result["makefile"].name == "Makefile"
