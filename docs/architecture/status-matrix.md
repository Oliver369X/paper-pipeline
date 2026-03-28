# Architecture status matrix (living)

| Área | Estado | Tests | Notas |
|------|--------|-------|--------|
| Mission contract v1/v2 | Implementado | `tests/test_mission_contract.py` | `mission_version` en `mission.md` |
| Run ledger | Implementado | `tests/test_run_ledger.py` | `outputs/run_ledger.json` |
| Preflight | Implementado | `tests/test_preflight_module.py` | `preflight_report.json` |
| Quality gates | Implementado | `tests/test_pipeline_mocked.py` | `validation/quality_validation.json` |
| Evidence bundle | Implementado | — | `evidence/evidence_index.json` |
| Publish decision | Implementado | `tests/test_server.py`, `tests/test_publication_signals.py` | `signals.py` + `publish_decision.json` |
| Métricas MetricsBundle + triaje | Implementado | `tests/test_triage_metrics_validation.py` | `metrics_io` + tier 0 si inválido; `PAPER_PIPELINE_RELAX_METRICS` → fallback `TriageMetrics` |
| Loop stall / stop | Implementado | `tests/test_integrated_loop_stop.py` | `outputs/loop/loop_state.json`, `stop_decision.json` |
| Packs research/code | Implementado | `tests/test_publication_packs.py` | `PAPER_PIPELINE_BUILD_PACKS=1` |
| Safety controller V1 | Implementado | `tests/test_safety_controller.py`, `tests/test_server.py` | `safety_trace.jsonl`, `GET .../safety/latest` |
| Objective State V1 | Implementado | `tests/test_objective_state.py`, `tests/test_server.py` | `objective_state.json`, `objective_trace.jsonl`, `GET .../objective/latest` |
| ResearchMemory V1 | Implementado | `tests/test_research_memory.py`, `tests/test_server.py` | `research_memory.jsonl`, `memory_index.json`, `GET .../memory/latest`, `GET .../memory/index` |
| Goal Selection V1 | Implementado | `tests/test_goal_selection.py`, `tests/test_server.py` | `goal_selection.json`, `GET .../goal-selection/latest` |
| API cockpit | Implementado | `tests/test_server.py` | publish/decision, loop/stop, metrics/validated, safety/latest, objective/latest, memory/latest, memory/index, goal-selection/latest |
| Agent eval harness V1 | Implementado | `tests/test_agent_eval_runner.py` | Escenarios JSON en `paper_pipeline/agent_eval/eval_scenarios/`, CLI `python -m paper_pipeline.agent_eval`, ver `docs/technical/agent-eval-spec.md` |
| Perplexity Strategy V1 | Implementado | `tests/test_perplexity_strategy.py` | Flag `PAPER_PIPELINE_PERPLEXITY_STRATEGY`, `outputs/perplexity_call_record.jsonl`, ver `docs/technical/perplexity-strategy-spec.md` |
| Memoria estratégica V2 (thin) | Implementado | `tests/test_strategic_memory.py` | `working_memory.json`, `hypotheses_registry.json`; hooks en `goal_selection` |
| Goal Manager V1 (goals.json) | Implementado | `tests/test_goals_manager.py`, `tests/test_goal_selection.py` | Semilla + override `in_progress`; `GET .../goals/latest` |
| Scheduler autonomía (dry-run) | Implementado | `tests/test_scheduler.py`, `tests/test_server.py` | `run_agent_step`, `agent_decisions.jsonl`, `POST .../agent/run-step`, CLI `paper-agent-step` |
| Safety policy pre/post | Implementado | `tests/test_safety_policy.py` | `policy_check_pre_goal`, `policy_check_post_action` |
| Memoria query / compact (stub) | Implementado | `tests/test_research_memory.py`, `tests/test_server.py` | `GET .../memory/query`, `POST .../memory/compact` |
| Web cockpit | Implementado | — | `/missions/:id/cockpit`; bloques agent decisions + Perplexity calls |
| Paralelo batch summary | Implementado | — | `outputs/batch_summary.json` |

Actualizar esta tabla al cambiar contratos o deprecar archivos.
