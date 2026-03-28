"""Tests mínimos del servidor FastAPI (sin Perplexity real)."""

from __future__ import annotations

import importlib
import time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PAPER_PIPELINE_DATA_DIR", str(tmp_path))
    import paper_pipeline.server.main as main_mod

    importlib.reload(main_mod)
    return TestClient(main_mod.app)


def test_invalid_mission_id_rejected(client: TestClient) -> None:
    r = client.get("/api/missions/foo..bar/draft")
    assert r.status_code == 400


def test_events_log_empty(client: TestClient) -> None:
    r = client.post(
        "/api/missions/",
        json={"title": "E", "topic": "t", "paper_target": "p"},
    )
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/events-log")
    assert r.status_code == 200
    assert r.json() == []


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["version"]
    assert data["perplexity_session"] in ("missing", "configured")
    assert data["notion"] in ("not_configured", "configured")
    assert data["brain_gemini"] in ("missing", "missing_sdk", "configured")


def test_models(client: TestClient) -> None:
    r = client.get("/api/models")
    assert r.status_code == 200
    data = r.json()
    assert "models" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) > 0


def test_section_keys(client: TestClient) -> None:
    r = client.get("/api/section-keys")
    assert r.status_code == 200
    data = r.json()
    assert "keys" in data
    assert "gaps" in data["keys"]
    assert "methodology" in data["keys"]
    assert "meta" in data and "gaps" in data["meta"]
    assert data["meta"]["gaps"]["output"] == "outputs/gaps.md"
    assert "outputs_help" in data and len(str(data["outputs_help"])) > 20


def test_list_missions_includes_flags_v2(client: TestClient) -> None:
    r = client.post(
        "/api/missions/",
        json={
            "title": "ListV2",
            "enable_hypervisor_triage": True,
            "enable_epistemic_injection": True,
            "enable_degradation_monitor": False,
            "enable_skill_orchestrator": False,
        },
    )
    assert r.status_code == 201
    mid = r.json()["id"]
    r = client.get("/api/missions/")
    assert r.status_code == 200
    items = r.json()
    row = next(x for x in items if x["id"] == mid)
    assert row["flags_v2"]["enable_hypervisor_triage"] is True
    assert row["flags_v2"]["enable_epistemic_injection"] is True
    assert row["flags_v2"]["enable_degradation_monitor"] is False
    assert row["flags_v2"]["enable_skill_orchestrator"] is False


@pytest.mark.filterwarnings("ignore:coroutine 'Queue.put' was never awaited:RuntimeWarning")
def test_mission_crud_and_run_dry(client: TestClient) -> None:
    r = client.post(
        "/api/missions/",
        json={"title": "T1", "topic": "X", "paper_target": "y", "sections_needed": ["a"]},
    )
    assert r.status_code == 201
    mid = r.json()["id"]

    r = client.get(f"/api/missions/{mid}")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == mid
    assert body["meta"]["title"] == "T1"

    r = client.post(f"/api/missions/{mid}/run?dry_run=true")
    assert r.status_code == 200
    assert "run_id" in r.json()

    for _ in range(100):
        time.sleep(0.05)
        r = client.get(f"/api/missions/{mid}/run-log")
        rows = r.json()
        if rows:
            assert isinstance(rows, list)
            break
    else:
        raise AssertionError("run.log no recibió eventos tras dry_run")


def test_draft_put_get(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "D"})
    mid = r.json()["id"]
    r = client.put(f"/api/missions/{mid}/draft", json={"content": "# Hola"})
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}/draft")
    assert r.json()["content"] == "# Hola"


@pytest.mark.filterwarnings("ignore:coroutine 'Queue.put' was never awaited:RuntimeWarning")
def test_mission_v2_flags_and_skill_manifest(client: TestClient, tmp_path) -> None:
    """API persiste flags v2; /run usa run_pipeline_v2 y escribe el manifiesto de skills."""
    r = client.post(
        "/api/missions/",
        json={
            "title": "V2",
            "topic": "Test topic for API",
            "enable_skill_orchestrator": True,
            "enable_epistemic_injection": False,
            "enable_degradation_monitor": False,
        },
    )
    assert r.status_code == 201
    mid = r.json()["id"]

    r = client.get(f"/api/missions/{mid}")
    assert r.status_code == 200
    m = r.json()["mission"]
    assert m["enable_skill_orchestrator"] is True
    assert m["enable_epistemic_injection"] is False

    r = client.post(f"/api/missions/{mid}/run?dry_run=true")
    assert r.status_code == 200

    manifest = tmp_path / mid / "outputs" / "skill_orchestrator_manifest.yaml"
    for _ in range(120):
        time.sleep(0.05)
        if manifest.is_file():
            break
    else:
        raise AssertionError("skill_orchestrator_manifest.yaml no apareció tras dry_run")

    assert "DOMAIN_ACQUISITION" in manifest.read_text(encoding="utf-8")


def test_patch_partial_preserves_v2_flags(client: TestClient) -> None:
    """PATCH with only topic must not reset enable_skill_orchestrator."""
    r = client.post(
        "/api/missions/",
        json={
            "title": "P",
            "topic": "T0",
            "enable_skill_orchestrator": True,
        },
    )
    mid = r.json()["id"]
    r = client.patch(f"/api/missions/{mid}", json={"topic": "T1"})
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}")
    m = r.json()["mission"]
    assert m["topic"] == "T1"
    assert m["enable_skill_orchestrator"] is True


def test_patch_explicit_false_disables_v2_flag(client: TestClient) -> None:
    r = client.post(
        "/api/missions/",
        json={
            "title": "Q",
            "topic": "Z",
            "enable_skill_orchestrator": True,
        },
    )
    mid = r.json()["id"]
    r = client.patch(
        f"/api/missions/{mid}",
        json={"enable_skill_orchestrator": False},
    )
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}")
    assert r.json()["mission"]["enable_skill_orchestrator"] is False


def test_patch_hypotheses_replace(client: TestClient) -> None:
    """PATCH replaces the full hypotheses list."""
    r = client.post("/api/missions/", json={"title": "Hyp", "topic": "t"})
    assert r.status_code == 201
    mid = r.json()["id"]
    r = client.patch(
        f"/api/missions/{mid}",
        json={
            "hypotheses": [
                {
                    "id": "h1",
                    "description": "D1",
                    "priority": "HIGH",
                    "expected_outcome": "E1",
                },
            ],
        },
    )
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}")
    hy = r.json()["mission"]["hypotheses"]
    assert len(hy) == 1
    assert hy[0]["id"] == "h1"
    assert hy[0]["description"] == "D1"


def test_export_missions_tsv(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "TSV", "topic": "x"})
    assert r.status_code == 201
    r = client.get("/api/missions/export.tsv")
    assert r.status_code == 200
    text = r.text
    assert "triage_tier" in text
    assert "hypotheses_count" in text
    assert "\t" in text


def test_patch_quality_gates_partial_merge(client: TestClient) -> None:
    """PATCH can update nested quality_gates; omitted nested keys preserve mission.md."""
    r = client.post("/api/missions/", json={"title": "QG", "topic": "t"})
    assert r.status_code == 201
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}")
    assert r.status_code == 200
    assert r.json()["mission"]["quality_gates"]["breakthrough_margin"] == 0.02
    assert r.json()["mission"]["quality_gates"]["replication_tolerance"] == 0.01

    r = client.patch(
        f"/api/missions/{mid}",
        json={"quality_gates": {"breakthrough_margin": 0.05}},
    )
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}")
    qg = r.json()["mission"]["quality_gates"]
    assert qg["breakthrough_margin"] == 0.05
    assert qg["replication_tolerance"] == 0.01


def test_patch_meta_only_does_not_resync_mission_defaults(client: TestClient) -> None:
    r = client.post(
        "/api/missions/",
        json={
            "title": "Old",
            "topic": "topic-x",
            "enable_skill_orchestrator": True,
        },
    )
    mid = r.json()["id"]
    r = client.patch(f"/api/missions/{mid}", json={"title": "New title only"})
    assert r.status_code == 200
    r = client.get(f"/api/missions/{mid}")
    assert r.json()["meta"]["title"] == "New title only"
    assert r.json()["mission"]["enable_skill_orchestrator"] is True
    assert r.json()["mission"]["topic"] == "topic-x"


def test_cockpit_ledger_404_without_run(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "C", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/ledger/latest")
    assert r.status_code == 404


def test_cockpit_publish_preview_empty(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "P", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.post(f"/api/missions/{mid}/publish/preview")
    assert r.status_code == 200
    assert r.json()["eligible"] is False


def test_cockpit_publish_decision_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "Pub", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/publish/decision")
    assert r.status_code == 404


def test_cockpit_loop_stop_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "L", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/loop/stop")
    assert r.status_code == 404


def test_cockpit_loop_stop_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "LS", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    stop = tmp_path / mid / "outputs" / "loop" / "stop_decision.json"
    stop.parent.mkdir(parents=True)
    stop.write_text(json.dumps({"status": "stopped", "reasons": ["x"]}), encoding="utf-8")
    r = client.get(f"/api/missions/{mid}/loop/stop")
    assert r.status_code == 200
    assert r.json()["status"] == "stopped"


def test_cockpit_metrics_validated_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "M", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/metrics/validated")
    assert r.status_code == 404


def test_cockpit_metrics_validated_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "MV", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    mp = tmp_path / mid / "outputs" / "metrics.json"
    mp.write_text(
        json.dumps(
            {"schema_version": 1, "exit_code": 0, "main": 0.5, "coverage": 0.8, "math_checks": "PASS"},
        ),
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/metrics/validated")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["errors"] == []


def test_cockpit_safety_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "S", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/safety/latest")
    assert r.status_code == 404


def test_cockpit_safety_latest_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "S2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    trace = tmp_path / mid / "outputs" / "safety_trace.jsonl"
    trace.write_text(
        json.dumps(
            {
                "decision": "BLOCK",
                "rule_id": "loop_stop_decision",
                "candidate_action": "loop_iteration",
            },
        )
        + "\n",
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/safety/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] == "BLOCK"
    assert body["rule_id"] == "loop_stop_decision"


def test_cockpit_objective_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "O", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/objective/latest")
    assert r.status_code == 404


def test_cockpit_objective_latest_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "O2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    op = tmp_path / mid / "outputs" / "objective_state.json"
    op.write_text(
        json.dumps(
            {
                "version": 1,
                "root_objective": "Maximizar evidencia reproducible",
                "status": "healthy",
                "utility_total": 0.5,
                "terms": {},
                "gates": {"publishable": True},
                "source_artifacts": [],
                "last_updated_at": "2026-03-26T00:00:00+00:00",
            },
        ),
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/objective/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["utility_total"] == 0.5


def test_cockpit_memory_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "M1", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/memory/latest")
    assert r.status_code == 404


def test_cockpit_memory_latest_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "M2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    mp = tmp_path / mid / "outputs" / "research_memory.jsonl"
    mp.write_text(
        json.dumps({"kind": "publish", "summary": "Publish elegible"}) + "\n",
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/memory/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["kind"] == "publish"
    assert body["summary"] == "Publish elegible"


def test_cockpit_memory_index_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "M3", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/memory/index")
    assert r.status_code == 404


def test_cockpit_memory_index_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "M4", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    mp = tmp_path / mid / "outputs" / "memory_index.json"
    mp.write_text(
        json.dumps(
            {
                "version": 1,
                "counts_by_kind": {"publish": 1},
                "last_event": {"kind": "publish"},
                "latest_by_kind": {"publish": {"summary": "ok"}},
                "source_artifacts": [],
                "last_updated_at": "2026-03-26T00:00:00+00:00",
            },
        ),
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/memory/index")
    assert r.status_code == 200
    body = r.json()
    assert body["counts_by_kind"]["publish"] == 1


def test_cockpit_goal_selection_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "G1", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.get(f"/api/missions/{mid}/goal-selection/latest")
    assert r.status_code == 404


def test_cockpit_goals_working_hypotheses_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "GH", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    assert client.get(f"/api/missions/{mid}/goals/latest").status_code == 404
    assert client.get(f"/api/missions/{mid}/working-memory/latest").status_code == 404
    assert client.get(f"/api/missions/{mid}/hypotheses/latest").status_code == 404


def test_cockpit_goals_working_hypotheses_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "GH2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    base = tmp_path / mid / "outputs"
    base.mkdir(parents=True, exist_ok=True)
    (base / "goals.json").write_text(
        json.dumps({"version": 1, "nodes": [], "mission_topic_hint": "t"}),
        encoding="utf-8",
    )
    (base / "working_memory.json").write_text(
        json.dumps(
            {
                "version": 1,
                "current_goal_type": "literature",
                "goal_text_snapshot": "x",
                "reason_snapshot": "y",
                "recent_observations": [],
                "constraints": {},
                "last_updated_at": "2026-03-27T00:00:00+00:00",
            },
        ),
        encoding="utf-8",
    )
    (base / "hypotheses_registry.json").write_text(
        json.dumps({"version": 1, "hypotheses": [], "last_updated_at": "2026-03-27T00:00:00+00:00"}),
        encoding="utf-8",
    )
    assert client.get(f"/api/missions/{mid}/goals/latest").status_code == 200
    assert client.get(f"/api/missions/{mid}/working-memory/latest").status_code == 200
    assert client.get(f"/api/missions/{mid}/hypotheses/latest").status_code == 200


def test_cockpit_goal_selection_latest_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "G2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    gp = tmp_path / mid / "outputs" / "goal_selection.json"
    gp.write_text(
        json.dumps(
            {
                "version": 1,
                "selected_goal_type": "verification",
                "goal_text": "Verificar bloqueos y claims",
                "priority": 0.9,
                "reason": "Hay bloqueos activos",
                "source_signals": ["objective_state.json", "memory_index.json"],
                "gates": {"publishable": False},
                "last_updated_at": "2026-03-26T00:00:00+00:00",
            },
        ),
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/goal-selection/latest")
    assert r.status_code == 200
    body = r.json()
    assert body["selected_goal_type"] == "verification"
    assert body["goal_text"] == "Verificar bloqueos y claims"


def test_cockpit_agent_decisions_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "AD", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    assert client.get(f"/api/missions/{mid}/agent/decisions/latest").status_code == 404


def test_cockpit_agent_decisions_latest_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "AD2", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    p = tmp_path / mid / "outputs" / "agent_decisions.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"dry_run": True, "would_execute": False}) + "\n", encoding="utf-8")
    r = client.get(f"/api/missions/{mid}/agent/decisions/latest")
    assert r.status_code == 200
    assert r.json()["dry_run"] is True


def test_cockpit_perplexity_calls_latest_404(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "PC", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    assert client.get(f"/api/missions/{mid}/perplexity/calls/latest").status_code == 404


def test_cockpit_memory_query_200(client: TestClient, tmp_path) -> None:
    import json

    r = client.post("/api/missions/", json={"title": "MQ", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    mp = tmp_path / mid / "outputs" / "research_memory.jsonl"
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(
        json.dumps(
            {
                "kind": "publish",
                "summary": "s",
                "tags": ["literature"],
                "payload": {},
            },
        )
        + "\n",
        encoding="utf-8",
    )
    r = client.get(f"/api/missions/{mid}/memory/query?goal_type=literature&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 1
    assert data["entries"][0]["tags"] == ["literature"]


def test_cockpit_memory_compact_200(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "MC", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.post(f"/api/missions/{mid}/memory/compact", json={"dry_run": True})
    assert r.status_code == 200
    body = r.json()
    assert body["dry_run"] is True
    assert "entries_total" in body
    assert body["request_dry_run"] is True


def test_cockpit_agent_run_step_200(client: TestClient) -> None:
    r = client.post("/api/missions/", json={"title": "RS", "topic": "t", "paper_target": "p"})
    mid = r.json()["id"]
    r = client.post(f"/api/missions/{mid}/agent/run-step", json={"dry_run": True})
    assert r.status_code == 200
    out = r.json()
    assert out["ok"] is True
    assert "record" in out
    assert out["record"]["dry_run"] is True
