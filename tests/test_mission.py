"""Tests for mission parsing."""

from __future__ import annotations

from pathlib import Path

from paper_pipeline.mission import Mission, load_mission


def test_load_mission_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "m.md"
    p.write_text(
        """---
topic: "Test topic"
paper_target: "ICLR"
sections_needed: [gaps]
max_perplexity_calls: 3
code_needed: false
enable_notion: false
model: best
---
""",
        encoding="utf-8",
    )
    m = load_mission(p)
    assert m.topic == "Test topic"
    assert m.sections_needed == ["gaps"]
    assert m.max_perplexity_calls == 3


def test_mission_defaults() -> None:
    m = Mission(topic="X", paper_target="Y")
    assert "related_work" in m.sections_needed
    assert m.enable_quality_check is True
    assert m.enable_cursor_cli is False
    assert m.save_perplexity_to_library is True
