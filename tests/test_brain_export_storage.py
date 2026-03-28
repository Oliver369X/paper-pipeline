"""Export Markdown del historial del cerebro."""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_pipeline.server import storage


def test_write_brain_conversation_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mid = "testexport123"

    def fake_mission_dir(m: str) -> Path:
        assert m == mid
        return tmp_path / m

    monkeypatch.setattr(storage, "mission_dir", fake_mission_dir)
    monkeypatch.setattr(storage, "read_brain_chat_history", lambda m, limit=200: [{"ts": "t1", "role": "user", "content": "hola"}, {"ts": "t2", "role": "assistant", "content": "hola2"}])

    p = storage.write_brain_conversation_export(mid)
    assert p.is_file()
    assert "hola" in p.read_text(encoding="utf-8")
    latest = tmp_path / mid / "outputs" / "brain_latest_export.md"
    assert latest.is_file()
