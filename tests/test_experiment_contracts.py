"""Contratos empíricos (tier, capability, fingerprint)."""

from __future__ import annotations

import json
from pathlib import Path

from paper_pipeline.pipeline.experiment_contracts import (
    TIER_FAILED,
    TIER_FULL_EMPIRICAL,
    TIER_PARTIAL_INFRASTRUCTURE,
    build_capability_contract,
    compute_empirical_fingerprint,
    enrich_metrics_json,
    infer_replication_tier,
)


def test_infer_tier_failed() -> None:
    assert infer_replication_tier({"exit_code": 1}) == TIER_FAILED


def test_infer_tier_fallback_hf() -> None:
    d = {
        "exit_code": 0,
        "experiment_runner": {"fallback_from_hf_import": True, "status": "ok"},
    }
    assert infer_replication_tier(d) == TIER_PARTIAL_INFRASTRUCTURE


def test_infer_tier_numpy_toy() -> None:
    d = {
        "exit_code": 0,
        "experiment_runner": {"status": "ok", "name": "numpy_linear_synthetic"},
    }
    assert infer_replication_tier(d) == TIER_PARTIAL_INFRASTRUCTURE


def test_infer_tier_hf_micro() -> None:
    d = {
        "exit_code": 0,
        "experiment_runner": {"status": "ok", "profile": "hf_llm_micro"},
    }
    assert infer_replication_tier(d) == TIER_FULL_EMPIRICAL


def test_enrich_writes_tier(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    p.write_text(
        json.dumps(
            {
                "exit_code": 0,
                "experiment_runner": {"status": "ok", "name": "numpy_linear_synthetic"},
            }
        ),
        encoding="utf-8",
    )
    enrich_metrics_json(tmp_path)
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("replication_tier") == TIER_PARTIAL_INFRASTRUCTURE
    assert "capability_contract" in data
    assert data["capability_contract"]["kfac_statistics"] == "unavailable"


def test_fingerprint_stable(tmp_path: Path) -> None:
    p = tmp_path / "metrics.json"
    payload = {
        "exit_code": 0,
        "replication_tier": TIER_PARTIAL_INFRASTRUCTURE,
        "experiment_runner": {
            "profile": "hf_llm_micro",
            "fallback_from_hf_import": True,
            "name": "numpy_linear_synthetic",
        },
    }
    p.write_text(json.dumps(payload), encoding="utf-8")
    a = compute_empirical_fingerprint(tmp_path)
    b = compute_empirical_fingerprint(tmp_path)
    assert a == b and len(a) == 20
