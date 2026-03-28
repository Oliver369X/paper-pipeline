"""Brain: Gemini mockeado, sin red."""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from paper_pipeline.brain.schemas import BrainChatMessage
from paper_pipeline.brain.service import run_brain_chat
from paper_pipeline.mission import Mission
from paper_pipeline.server.schemas import MissionPatch


def _fake_raw() -> dict:
    return {
        "reply": "Listo: propongo secciones y brief.",
        "brief_markdown": "## Línea de investigación\n\nContexto doctoral de prueba.",
        "followup_questions": ["¿Qué dataset usarías?", "¿Baseline mínimo?"],
        "meta": {"title": "Título auto", "description": "Desc"},
        "mission": {
            "topic": "Tema de prueba",
            "paper_target": "NeurIPS",
            "sections_needed": ["gaps", "methodology"],
            "max_perplexity_calls": 8,
            "enable_quality_check": True,
            "model": "best",
            "language": "es-ES",
        },
    }


def test_suggested_from_raw_merges_top_level_hypotheses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gemini a veces pone ``hypotheses`` en la raíz del JSON, no dentro de ``mission``."""

    from paper_pipeline.brain import service as svc

    raw = {
        **_fake_raw(),
        "mission": {"topic": "Tema de prueba"},
        "hypotheses": [{"statement": "H1 desde raíz"}, {"statement": "H2 desde raíz"}],
    }
    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: raw)

    out = run_brain_chat(
        [BrainChatMessage(role="user", content="Hipótesis en raíz")],
        mission=None,
        meta_title="",
        meta_description="",
    )
    hp = out.suggested_patch.get("hypotheses")
    assert isinstance(hp, list) and len(hp) == 2
    assert hp[0]["description"] == "H1 desde raíz"


def test_run_brain_chat_normalizes_hypotheses_statement_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    """El modelo a veces devuelve ``statement`` en vez de ``id``/``description``."""

    from paper_pipeline.brain import service as svc

    raw = {
        **_fake_raw(),
        "mission": {
            **_fake_raw()["mission"],
            "hypotheses": [
                {"statement": "La integración reduce la perplejidad."},
                {"statement": "El unlearning baja al menos un 20% en perplejidad."},
            ],
        },
    }
    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: raw)

    out = run_brain_chat(
        [BrainChatMessage(role="user", content="Hipótesis")],
        mission=None,
        meta_title="",
        meta_description="",
    )
    hp = out.suggested_patch.get("hypotheses")
    assert isinstance(hp, list) and len(hp) == 2
    assert hp[0]["id"] == "hyp-1"
    assert "perplejidad" in hp[0]["description"].lower()
    assert hp[1]["id"] == "hyp-2"


def test_run_brain_chat_maps_patch(monkeypatch: pytest.MonkeyPatch) -> None:
    from paper_pipeline.brain import service as svc

    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: _fake_raw())

    m = Mission(
        topic="old",
        paper_target="old",
        sections_needed=["gaps"],
        max_perplexity_calls=4,
    )
    out = run_brain_chat(
        [BrainChatMessage(role="user", content="Quiero replicar un paper sobre X")],
        mission=m,
        meta_title="Old",
        meta_description="",
    )
    assert out.suggested_patch.get("topic") == "Tema de prueba"
    assert out.suggested_patch.get("title") == "Título auto"
    assert len(out.brief_markdown) > 10
    assert len(out.followup_questions) == 2


def test_run_brain_chat_retries_on_generate_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from paper_pipeline.brain import service as svc

    calls: list[int] = []

    def flaky(system_instruction: str, user_text: str) -> dict:
        calls.append(1)
        if len(calls) == 1:
            raise ValueError("simulated API error")
        return _fake_raw()

    monkeypatch.setattr(svc, "generate_brain_json", flaky)

    out = run_brain_chat(
        [BrainChatMessage(role="user", content="Hola")],
        mission=None,
        meta_title="",
        meta_description="",
    )
    assert len(calls) == 2
    assert out.reply


def test_run_brain_chat_retries_on_patch_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Primer JSON inválido para MissionPatch → segundo intento con datos buenos."""
    from paper_pipeline.brain import service as svc

    calls: list[int] = []

    def flaky(system_instruction: str, user_text: str) -> dict:
        calls.append(1)
        if len(calls) == 1:
            return {
                "reply": "x",
                "brief_markdown": "",
                "meta": {},
                "mission": {"max_perplexity_calls": 0},
            }
        return _fake_raw()

    monkeypatch.setattr(svc, "generate_brain_json", flaky)

    out = run_brain_chat(
        [BrainChatMessage(role="user", content="Hola")],
        mission=None,
        meta_title="",
        meta_description="",
    )
    assert len(calls) == 2
    assert out.suggested_patch.get("topic") == "Tema de prueba"


def test_mission_patch_empty_body() -> None:
    """Solo brief: patch vacío es válido y no aplica cambios a mission."""
    p = MissionPatch()
    assert p.model_dump(exclude_unset=True) == {}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPER_PIPELINE_DATA_DIR", str(tmp_path))
    import paper_pipeline.server.main as main_mod

    importlib.reload(main_mod)
    return TestClient(main_mod.app)


def test_brain_chat_503_without_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/chat",
        json={"messages": [{"role": "user", "content": "hola"}]},
    )
    assert r2.status_code == 503


def test_brain_chat_503_without_sdk(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-present")
    from paper_pipeline.server.routers import missions_brain as mb

    monkeypatch.setattr(mb, "brain_sdk_available", lambda: False)
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/chat",
        json={"messages": [{"role": "user", "content": "hola"}]},
    )
    assert r2.status_code == 503
    assert "google-genai" in (r2.json().get("detail") or "")


def test_brain_chat_200_with_mock_gemini(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-for-mock")
    from paper_pipeline.brain import service as svc

    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: _fake_raw())

    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/chat",
        json={"messages": [{"role": "user", "content": "hola"}]},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["reply"]
    assert "brief_markdown" in data
    assert data["suggested_patch"].get("topic") == "Tema de prueba"
    assert "cursor_checklist_markdown" in data


def test_brain_apply_and_run_returns_run_id(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_spawn(mid: str, loop, *, dry_run: bool = False) -> str:
        return "applyrun01"

    monkeypatch.setattr(
        "paper_pipeline.server.routers.missions_brain.spawn_pipeline_run",
        fake_spawn,
    )
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/apply_and_run",
        json={
            "patch": {},
            "brief_markdown": "## Brief\n",
            "dry_run": False,
        },
    )
    assert r2.status_code == 200
    assert r2.json()["run_id"] == "applyrun01"


def test_brain_apply_run_pipeline_returns_run_id(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_spawn(mid: str, loop, *, dry_run: bool = False) -> str:
        return "deadbeefcafe"

    monkeypatch.setattr(
        "paper_pipeline.server.routers.missions_brain.spawn_pipeline_run",
        fake_spawn,
    )
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/apply",
        json={
            "patch": {},
            "brief_markdown": "## Brief\n",
            "run_pipeline": True,
            "dry_run": False,
        },
    )
    assert r2.status_code == 200
    assert r2.json()["run_id"] == "deadbeefcafe"


def test_brain_apply_without_run_pipeline_run_id_null(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/apply",
        json={"patch": {}, "brief_markdown": "", "run_pipeline": False},
    )
    assert r2.status_code == 200
    assert r2.json().get("run_id") is None


def test_brain_apply_empty_patch_writes_brief_only(client: TestClient, tmp_path) -> None:
    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/apply",
        json={"patch": {}, "brief_markdown": "## Solo brief\n"},
    )
    assert r2.status_code == 200
    brief_path = tmp_path / mid / "outputs" / "brain_brief.md"
    assert brief_path.is_file()
    assert "Solo brief" in brief_path.read_text(encoding="utf-8")
    mem = tmp_path / mid / "outputs" / "research_memory.jsonl"
    assert mem.is_file()


def test_brain_chat_appends_history_jsonl(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-for-mock")
    from paper_pipeline.brain import service as svc

    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: _fake_raw())

    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/chat",
        json={"messages": [{"role": "user", "content": "hola"}]},
    )
    assert r2.status_code == 200
    hist = client.get(f"/api/missions/{mid}/brain/history")
    assert hist.status_code == 200
    msgs = hist.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user" and msgs[0]["content"] == "hola"
    assert msgs[1]["role"] == "assistant"


def test_brain_history_delete(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-for-mock")
    from paper_pipeline.brain import service as svc

    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: _fake_raw())

    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    client.post(
        f"/api/missions/{mid}/brain/chat",
        json={"messages": [{"role": "user", "content": "x"}]},
    )
    d = client.delete(f"/api/missions/{mid}/brain/history")
    assert d.status_code == 200
    h = client.get(f"/api/missions/{mid}/brain/history")
    assert h.json()["messages"] == []


def _variant_raw(n: int) -> dict:
    def one(i: int) -> dict:
        return {
            "label": f"V{i}",
            "short_rationale": "r",
            "brief_markdown": f"## B{i}",
            "meta": {"title": "T", "description": "D"},
            "mission": {
                "topic": f"t{i}",
                "paper_target": "iclr",
                "sections_needed": ["gaps", "methodology"],
                "max_perplexity_calls": 8,
            },
        }

    return {"variants": [one(i) for i in range(n)]}


def test_brain_variants_200(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key-for-mock")
    from paper_pipeline.brain import service as svc

    monkeypatch.setattr(svc, "generate_brain_json", lambda system_instruction, user_text: _variant_raw(3))

    r = client.post("/api/missions/", json={"title": "B", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r2 = client.post(
        f"/api/missions/{mid}/brain/variants",
        json={"n": 3, "messages": [{"role": "user", "content": "ideas"}]},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert len(data["variants"]) == 3
    assert data["variants"][0]["label"] == "V0"


def test_run_brain_chat_brief_in_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    from paper_pipeline.brain import service as svc

    captured: list[str] = []

    def capture(system_instruction: str, user_text: str) -> dict:
        captured.append(user_text)
        return _fake_raw()

    monkeypatch.setattr(svc, "generate_brain_json", capture)

    run_brain_chat(
        [BrainChatMessage(role="user", content="Hola")],
        mission=None,
        meta_title="",
        meta_description="",
        persisted_brief="## Brief anterior guardado",
    )
    assert captured
    assert "Brief persistido" in captured[0]
    assert "Brief anterior guardado" in captured[0]


def test_run_brain_chat_memory_context_in_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    from paper_pipeline.brain import service as svc

    captured: list[str] = []

    def capture(system_instruction: str, user_text: str) -> dict:
        captured.append(user_text)
        return _fake_raw()

    monkeypatch.setattr(svc, "generate_brain_json", capture)

    run_brain_chat(
        [BrainChatMessage(role="user", content="Hola")],
        mission=None,
        meta_title="",
        meta_description="",
        memory_context="- abc brain_brief: resumen de memoria",
    )
    assert captured
    assert "Memoria contextual" in captured[0]
    assert "resumen de memoria" in captured[0]
