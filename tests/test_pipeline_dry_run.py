"""Dry-run behavior: no Perplexity client, no draft files."""

from __future__ import annotations

from paper_pipeline.orchestrator import run_pipeline


def test_dry_run_no_draft_without_token(
    minimal_mission: Path,
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("PERPLEXITY_SESSION_TOKEN", raising=False)
    out_abs = (tmp_path / "out_dr").resolve()
    raw = minimal_mission.read_text(encoding="utf-8").replace(
        'output_dir: "outputs"',
        f'output_dir: "{out_abs.as_posix()}"',
    )
    minimal_mission.write_text(raw, encoding="utf-8")

    code = run_pipeline(minimal_mission, dry_run=True)
    assert code == 0
    assert not (out_abs / "draft_paper.md").exists()


def test_dry_run_no_draft_even_with_token(
    minimal_mission: Path,
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("PERPLEXITY_SESSION_TOKEN", "fake-token-for-test")
    out_abs = (tmp_path / "out_dr2").resolve()
    raw = minimal_mission.read_text(encoding="utf-8").replace(
        'output_dir: "outputs"',
        f'output_dir: "{out_abs.as_posix()}"',
    )
    minimal_mission.write_text(raw, encoding="utf-8")

    code = run_pipeline(minimal_mission, dry_run=True)
    assert code == 0
    assert not (out_abs / "draft_paper.md").exists()
