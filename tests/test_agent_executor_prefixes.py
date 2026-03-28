"""``parallel_allowed_command_prefixes`` en mission.md vs entorno."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.parallel.agent_executor import _prefixes_from_mission, allowed_command_prefixes


def test_prefixes_from_mission_overrides_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_PARALLEL_CMD_PREFIXES", "echo,date")
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / "mission.md").write_text(
        "---\n"
        "topic: t\n"
        "paper_target: p\n"
        "parallel_allowed_command_prefixes: [python, pytest]\n"
        "---\n",
        encoding="utf-8",
    )
    assert _prefixes_from_mission(wt) == ("python", "pytest")


def test_prefixes_from_mission_empty_list_falls_back_to_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_PARALLEL_CMD_PREFIXES", "echo,date")
    wt = tmp_path / "wt"
    wt.mkdir()
    (wt / "mission.md").write_text(
        "---\n"
        "topic: t\n"
        "paper_target: p\n"
        "parallel_allowed_command_prefixes: []\n"
        "---\n",
        encoding="utf-8",
    )
    assert _prefixes_from_mission(wt) == ("echo", "date")


def test_prefixes_from_mission_missing_file_uses_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PAPER_PIPELINE_PARALLEL_CMD_PREFIXES", "foo")
    wt = tmp_path / "empty"
    wt.mkdir()
    assert _prefixes_from_mission(wt) == ("foo",)


def test_allowed_command_prefixes_unset_uses_default(monkeypatch) -> None:
    monkeypatch.delenv("PAPER_PIPELINE_PARALLEL_CMD_PREFIXES", raising=False)
    assert allowed_command_prefixes() == ("python", "python3", "pytest", "uv", "pip")
