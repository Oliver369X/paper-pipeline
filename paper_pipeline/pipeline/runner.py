"""Main ``run_pipeline`` coordinator."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path

from perplexity_webui_scraper import ClientConfig, Perplexity

from paper_pipeline.config.mission_contract import MissionValidationError, validate_mission_contract
from paper_pipeline.constants import ExitCode
from paper_pipeline.evidence.bundle_builder import build_evidence_bundle
from paper_pipeline.agent.goal_selection import update_goal_selection_artifacts
from paper_pipeline.agent.objective_state import update_objective_artifacts
from paper_pipeline.agent.research_memory import append_research_memory
from paper_pipeline.ledger.writer import LedgerWriter
from paper_pipeline.logger import PipelineLogger
from paper_pipeline.manifest import PipelineManifest, new_manifest
from paper_pipeline.mission import Mission, load_mission
from paper_pipeline.publication.publish_manager import write_publish_decision
from paper_pipeline.state import RunState, state_path_for
from paper_pipeline.pipeline.provenance import write_pipeline_provenance_json
from paper_pipeline.validation.claim_extractor import (
    write_claim_provenance,
    write_claims_evidence_checklist,
    write_claims_json,
)
from paper_pipeline.validation.quality_gate_runner import run_quality_gates, write_quality_validation

from .assembly_phase import run_assembly
from .common import (
    build_conversation_config,
    build_mimo_client,
    build_mistral_client,
    count_prior_perplexity_calls,
)
from .lessons_learned_phase import run_lessons_learned_phase
from paper_pipeline.literature.arxiv_fetch import run_literature_ingest_phase
from .mistral_phase import run_mistral_sections
from .research_agent_phase import run_research_agent_phase
from .research_map import write_research_map
from .research_plan_phase import run_research_plan_phase
from .source_curation import run_source_curation_phase
from .notion_phase import run_notion_phase
from .perplexity_phase import run_perplexity_sections
from .mimo_phase import run_mimo_sections
from .preflight import run_preflight, write_preflight_report
from .experiment_iteration import (
    run_post_cursor_experiment_iteration,
    should_defer_experiment_until_after_cursor,
)
from .experiment_phase import (
    ExperimentRunnerResult,
    TIER_NOT_RUN,
    run_experiment_runner_phase,
)
from .experiment_contracts import (
    TIER_PARTIAL_INFRASTRUCTURE,
    TIER_PLANNING_ONLY,
    compute_empirical_fingerprint,
    maybe_invalidate_on_empirical_fingerprint_change,
)
from .quality_phase import run_quality_phase
from .replication_status import write_degraded_replication_artifacts, write_replication_artifacts
from .run_state_policy import (
    experiment_runner_config_hash,
    invalidate_resume_after_critical_failure,
    invalidate_resume_if_experiment_runner_config_changed,
)

logger = logging.getLogger(__name__)


def _cursor_cli_failure_optional(mission: Mission) -> bool:
    """Si True, un fallo del agente no aborta el run (ver ``PAPER_PIPELINE_CURSOR_CLI_OPTIONAL``)."""

    if mission.cursor_cli_optional:
        return True
    return os.environ.get("PAPER_PIPELINE_CURSOR_CLI_OPTIONAL", "").lower() in ("1", "true", "yes")


def _should_block_on_experiment_failure(mission: Mission) -> bool:
    if not mission.enable_experiment_runner:
        return False
    env = os.environ.get("PAPER_PIPELINE_STRICT_EXPERIMENT", "").strip().lower()
    if env in ("1", "true", "yes"):
        return True
    if env in ("0", "false", "no"):
        return False
    return mission.experiment_runner.block_pipeline_on_failure

_LEDGER_PHASES = [
    "mission_validation",
    "preflight",
    "perplexity_sections",
    "assembly_draft",
    "experiment_runner",
    "quality_check",
    "notion_sync",
    "cursor_cli",
    "final_decision",
]


def run_pipeline(
    mission_path: Path,
    *,
    dry_run: bool = False,
    event_sink: Callable[[dict], None] | None = None,
) -> int:
    """Run full pipeline. Returns process exit code."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        mission = load_mission(mission_path)
    except (OSError, ValueError) as exc:
        logger.error("Invalid mission file: %s", exc)
        return ExitCode.ERROR

    out = Path(mission.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    code_dir = out / "code"
    code_dir.mkdir(parents=True, exist_ok=True)

    try:
        validate_mission_contract(mission)
    except MissionValidationError as exc:
        logger.error("Mission contract validation failed: %s", exc)
        return ExitCode.ERROR

    mission_id = mission_path.resolve().parent.name or "mission"
    ledger = LedgerWriter(out, mission_path=mission_path)
    ledger.start(
        mission_id=mission_id,
        mission_version=mission.mission_version,
        phase_names=_LEDGER_PHASES,
    )
    ledger.upsert_phase("mission_validation", "done")

    manifest = new_manifest()
    manifest.write(out)

    plog = PipelineLogger(out, on_event=event_sink)
    state_path = state_path_for(out)
    state = RunState.load(state_path)

    plog.step_start("pipeline", mission=str(mission_path), topic=mission.topic, dry_run=dry_run)

    maybe_invalidate_on_empirical_fingerprint_change(state, state_path, out)
    invalidate_resume_if_experiment_runner_config_changed(mission, state, state_path)

    if mission.provider not in ("xiaomi_mimo", "mistral"):
        try:
            build_conversation_config(mission)
        except ValueError as exc:
            logger.error("%s", exc)
            plog.step_error("pipeline", error="invalid_mission_model", detail=str(exc))
            ledger.upsert_phase("mission_validation", "failed", error=str(exc))
            ledger.finalize("failed")
            return ExitCode.ERROR

    ledger.upsert_phase("preflight", "running")
    pf = run_preflight(
        output_dir=out,
        dry_run=dry_run,
        require_cursor_if_enabled=True,
        cursor_enabled=bool(mission.code_needed and mission.enable_cursor_cli),
    )
    write_preflight_report(out, pf)
    if not pf.ok:
        logger.error("Preflight failed: %s", pf.blocking_reasons)
        plog.step_error("pipeline", error="preflight_failed", detail="; ".join(pf.blocking_reasons))
        ledger.upsert_phase("preflight", "failed", error="; ".join(pf.blocking_reasons))
        ledger.finalize("failed")
        return ExitCode.ERROR
    ledger.upsert_phase("preflight", "done")

    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    xiaomi_token = os.environ.get("XIAOMI_API_KEY", "").strip()
    mistral_token = os.environ.get("MISTRAL_API_KEY", "").strip()

    if mission.provider == "mistral":
        if not mistral_token and not dry_run:
            logger.error("MISTRAL_API_KEY is not set")
            plog.step_error("pipeline", error="mistral_auth_error", detail="MISTRAL_API_KEY missing")
            ledger.upsert_phase("preflight", "failed", error="missing MISTRAL_API_KEY")
            ledger.finalize("failed")
            return ExitCode.PERPLEXITY_AUTH_ERROR
    elif mission.provider == "xiaomi_mimo":
        if not xiaomi_token and not dry_run:
            logger.error("XIAOMI_API_KEY is not set")
            plog.step_error("pipeline", error="xiaomi_auth_error", detail="XIAOMI_API_KEY missing")
            ledger.upsert_phase("preflight", "failed", error="missing XIAOMI_API_KEY")
            ledger.finalize("failed")
            return ExitCode.PERPLEXITY_AUTH_ERROR
    else:
        if not token and not dry_run:
            logger.error("PERPLEXITY_SESSION_TOKEN is not set")
            plog.step_error("pipeline", error="perplexity_auth_error", detail="PERPLEXITY_SESSION_TOKEN missing")
            ledger.upsert_phase("preflight", "failed", error="missing PERPLEXITY_SESSION_TOKEN")
            ledger.finalize("failed")
            return ExitCode.PERPLEXITY_AUTH_ERROR

    ctx = {
        "topic": mission.topic,
        "paper_target": mission.paper_target,
    }

    if not dry_run and not mission.save_perplexity_to_library:
        logger.warning(
            "save_perplexity_to_library=false: Perplexity SSE uses incognito (is_incognito=true); "
            "new threads often do not appear in web Library/history. Set true for visible chats."
        )

    calls_used = count_prior_perplexity_calls(state, mission)
    written: list[tuple[str, Path]] = []

    if dry_run:
        logger.info("Dry run: would write %s sections for topic=%r", len(mission.sections_needed), mission.topic)
        plog.step_ok("pipeline", dry_run=True, sections=len(mission.sections_needed))
        ledger.upsert_phase("final_decision", "done", meta={"dry_run": True})
        ledger.finalize("completed")
        return ExitCode.OK

    ledger.upsert_phase("perplexity_sections", "running")

    client = None
    mimo_client = None
    mistral_client = None
    shared_conversation = None

    try:
        run_literature_ingest_phase(mission, out, plog, manifest=manifest)

        if mission.provider == "mistral":
            mistral_client = build_mistral_client(mission)
            agent_code = run_research_agent_phase(
                mission, mistral_client, out, plog, manifest=manifest
            )
            if agent_code != 0:
                ledger.upsert_phase("perplexity_sections", "failed", error="research_agent failed")
                ledger.finalize("failed")
                return ExitCode.ERROR

            calls_used, plan_code = run_research_plan_phase(
                mission,
                mistral_client,
                state,
                state_path,
                out,
                plog,
                calls_used,
                manifest=manifest,
            )
            if plan_code != 0:
                ledger.upsert_phase("perplexity_sections", "failed", error="research_plan failed")
                ledger.finalize("failed")
                return ExitCode.ERROR

            calls_used, p_code = run_mistral_sections(
                mission,
                mistral_client,
                state,
                state_path,
                out,
                plog,
                calls_used,
                written,
                event_sink=event_sink,
                manifest=manifest,
            )
            if p_code != 0:
                ledger.upsert_phase("perplexity_sections", "failed", error="mistral phase failed")
                ledger.finalize("failed")
                return ExitCode.ERROR
            ledger.upsert_phase("perplexity_sections", "done")

            run_source_curation_phase(
                mission,
                out,
                written,
                plog,
                manifest=manifest,
                mistral_client=mistral_client,
            )
        elif mission.provider == "xiaomi_mimo":
            mimo_client = build_mimo_client(mission)
            calls_used, p_code = run_mimo_sections(
                mission,
                mimo_client,
                state,
                state_path,
                out,
                plog,
                calls_used,
                written,
                event_sink=event_sink,
                manifest=manifest,
            )
            if p_code != 0:
                ledger.upsert_phase("perplexity_sections", "failed", error="mimo phase failed")
                ledger.finalize("failed")
                return ExitCode.ERROR
            ledger.upsert_phase("perplexity_sections", "done")
        else:
            client = Perplexity(token, config=ClientConfig())

            if mission.single_thread_perplexity:
                logger.info("Perplexity mode: single thread (sections share one conversation)")
            else:
                if state.perplexity_backend_uuid is not None or state.perplexity_read_write_token is not None:
                    state.perplexity_backend_uuid = None
                    state.perplexity_read_write_token = None
                    state.save(state_path)

            calls_used, shared_conversation, p_code = run_perplexity_sections(
                mission,
                client,
                state,
                state_path,
                out,
                plog,
                calls_used,
                written,
                event_sink=event_sink,
                manifest=manifest,
            )
            if p_code != 0:
                ledger.upsert_phase("perplexity_sections", "failed", error="perplexity phase failed")
                ledger.finalize("failed")
                return ExitCode.ERROR
            ledger.upsert_phase("perplexity_sections", "done")

            run_source_curation_phase(
                mission,
                out,
                written,
                plog,
                manifest=manifest,
                mistral_client=None,
            )

        ledger.upsert_phase("assembly_draft", "running")
        draft_path = run_assembly(
            mission,
            out,
            code_dir,
            written,
            state,
            state_path,
            plog,
            event_sink=event_sink,
            manifest=manifest,
        )
        ledger.upsert_phase("assembly_draft", "done")

        ledger.upsert_phase("experiment_runner", "running")
        if should_defer_experiment_until_after_cursor(mission):
            exp_res = ExperimentRunnerResult(ok=True, exit_code=0, replication_tier=TIER_NOT_RUN)
            plog.step_skip("experiment_runner", reason="deferred_until_after_cursor")
            ledger.upsert_phase("experiment_runner", "done", meta={"deferred": True})
        else:
            exp_res = run_experiment_runner_phase(mission, out, plog, mission_path=mission_path)
            if not exp_res.ok:
                ledger.upsert_phase("experiment_runner", "failed", error=exp_res.reason or "failed")
            else:
                ledger.upsert_phase("experiment_runner", "done")
                if mission.enable_experiment_runner:
                    state.empirical_fingerprint = compute_empirical_fingerprint(out)
                    state.experiment_runner_config_hash = experiment_runner_config_hash(mission.experiment_runner)
                    state.save(state_path)

        if (
            mission.enable_experiment_runner
            and exp_res.ok
            and exp_res.replication_tier in (TIER_PARTIAL_INFRASTRUCTURE, TIER_PLANNING_ONLY)
        ):
            write_degraded_replication_artifacts(out, draft_path, exp_res, mission_topic=mission.topic)

        if (
            mission.enable_experiment_runner
            and _should_block_on_experiment_failure(mission)
            and not exp_res.ok
        ):
            write_replication_artifacts(out, draft_path, exp_res, mission_topic=mission.topic)
            invalidate_resume_after_critical_failure(state, state_path, cause="experiment_runner")
            plog.step_error(
                "pipeline",
                error="experiment_runner_blocked",
                detail=exp_res.reason or "",
            )
            ledger.finalize("failed")
            return ExitCode.ERROR

        ledger.upsert_phase("quality_check", "running")
        if mission.provider == "mistral":
            calls_used, q_code = run_quality_phase(
                mission,
                None,
                None,
                state,
                state_path,
                out,
                draft_path,
                plog,
                calls_used,
                written,
                ctx,
                manifest=manifest,
                mistral_client=mistral_client,
            )
        elif mission.provider == "xiaomi_mimo":
            calls_used, q_code = run_quality_phase(
                mission,
                None,
                None,
                state,
                state_path,
                out,
                draft_path,
                plog,
                calls_used,
                written,
                ctx,
                manifest=manifest,
                mimo_client=mimo_client,
            )
        else:
            calls_used, q_code = run_quality_phase(
                mission,
                client,
                shared_conversation,
                state,
                state_path,
                out,
                draft_path,
                plog,
                calls_used,
                written,
                ctx,
                manifest=manifest,
            )
        if q_code != 0:
            ledger.upsert_phase("quality_check", "failed", error="quality phase failed")
            ledger.finalize("failed")
            return ExitCode.ERROR

        gates_ok, gate_report = run_quality_gates(mission, out)
        write_quality_validation(out, gate_report)
        append_research_memory(
            out,
            kind="quality",
            summary="Quality gates OK" if gates_ok else "Quality gates con bloqueos",
            source_artifacts=["validation/quality_validation.json"],
            payload=gate_report if isinstance(gate_report, dict) else {"value": gate_report},
            tags=["quality", "publishable" if gates_ok else "blocked"],
            confidence=0.8,
        )
        write_claims_json(out, draft_path)
        write_claims_evidence_checklist(out, draft_path, mission=mission)
        write_claim_provenance(out, draft_path, mission=mission)
        if mission.mission_version >= 2 and not gates_ok:
            plog.step_error("pipeline", error="quality_gates_failed", detail=str(gate_report.get("blocking_reasons")))
            ledger.upsert_phase("quality_check", "failed", error="quality gates")
            ledger.finalize("failed")
            return ExitCode.ERROR
        ledger.upsert_phase("quality_check", "done")

        ledger.upsert_phase("notion_sync", "running")
        n_code = run_notion_phase(
            mission,
            out,
            code_dir,
            written,
            state,
            state_path,
            plog,
            event_sink=event_sink,
            manifest=manifest,
        )
        if n_code != 0:
            ledger.upsert_phase("notion_sync", "failed", error=f"exit {n_code}")
            ledger.finalize("failed")
            return n_code
        ledger.upsert_phase("notion_sync", "done")

        if not (mission.code_needed and mission.enable_cursor_cli):
            if manifest:
                manifest.upsert_phase("cursor_cli", "skipped")
                manifest.write(out)
            ledger.upsert_phase("cursor_cli", "skipped")
        elif mission.code_needed and mission.enable_cursor_cli:
            from paper_pipeline.cursor_cli_runner import run_cursor_cli

            if state.already_done("step:cursor_cli"):
                plog.step_skip("step:cursor_cli", reason="already completed in previous run")
                ledger.upsert_phase("cursor_cli", "skipped", meta={"reason": "already_done"})
            else:
                if manifest:
                    manifest.upsert_phase("cursor_cli", "running")
                    manifest.write(out)
                mission_dir = mission_path.resolve().parent
                cwd = Path(mission.cursor_cli_cwd).resolve() if mission.cursor_cli_cwd else mission_dir
                prompt_path: Path | None = None
                if mission.cursor_cli_prompt_path:
                    candidate = (mission_dir / mission.cursor_cli_prompt_path).resolve()
                    if candidate.is_file():
                        prompt_path = candidate
                    else:
                        logger.warning("cursor_cli_prompt_path not found: %s (using auto prompt)", candidate)

                plog.step_start("step:cursor_cli")
                cli_code = run_cursor_cli(
                    cwd=cwd,
                    output_dir=out,
                    mission=mission,
                    prompt_file=prompt_path,
                    dry_run=False,
                    pipeline_log=plog,
                )
                if cli_code != 0:
                    plog.step_error(
                        "step:cursor_cli",
                        error="cursor_cli_failed",
                        exit_code=cli_code,
                        detail="Ver outputs/cursor_cli_diagnostics.json y outputs/cursor_cli.log",
                    )
                    if _cursor_cli_failure_optional(mission):
                        logger.warning(
                            "Cursor CLI falló (exit %s) pero el paso es opcional; el run continúa. "
                            "Definí cursor_cli_optional en mission.md o PAPER_PIPELINE_CURSOR_CLI_OPTIONAL=1 en .env.",
                            cli_code,
                        )
                        if manifest:
                            manifest.upsert_phase("cursor_cli", "failed", error=f"exit {cli_code} (optional)")
                            manifest.write(out)
                        ledger.upsert_phase(
                            "cursor_cli",
                            "failed",
                            error=f"exit {cli_code} (optional, run continued)",
                        )
                    else:
                        invalidate_resume_after_critical_failure(state, state_path, cause="cursor_cli")
                        if manifest:
                            manifest.upsert_phase("cursor_cli", "failed", error=f"exit {cli_code}")
                            manifest.write(out)
                        ledger.upsert_phase("cursor_cli", "failed", error=f"exit {cli_code}")
                        ledger.finalize("failed")
                        return cli_code
                else:
                    plog.step_ok("step:cursor_cli")
                    state.mark_done("step:cursor_cli")
                    state.save(state_path)
                    if manifest:
                        manifest.upsert_phase("cursor_cli", "done")
                        manifest.write(out)
                    ledger.upsert_phase("cursor_cli", "done")

                    if should_defer_experiment_until_after_cursor(mission):
                        exp_res, calls_used = run_post_cursor_experiment_iteration(
                            mission,
                            mission_path,
                            out,
                            plog,
                            client,
                            calls_used,
                        )
                        if exp_res.ok and mission.enable_experiment_runner:
                            state.empirical_fingerprint = compute_empirical_fingerprint(out)
                            state.experiment_runner_config_hash = experiment_runner_config_hash(
                                mission.experiment_runner
                            )
                            state.save(state_path)
                        if (
                            mission.enable_experiment_runner
                            and _should_block_on_experiment_failure(mission)
                            and not exp_res.ok
                        ):
                            draft_path = out / "draft_paper.md"
                            write_replication_artifacts(
                                out, draft_path, exp_res, mission_topic=mission.topic
                            )
                            invalidate_resume_after_critical_failure(
                                state, state_path, cause="experiment_iteration"
                            )
                            plog.step_error(
                                "pipeline",
                                error="experiment_iteration_blocked",
                                detail=exp_res.reason or "",
                            )
                            ledger.finalize("failed")
                            return ExitCode.ERROR

    finally:
        if client is not None:
            client.close()

    run_lessons_learned_phase(mission, out, plog, mistral_client=mistral_client)
    write_research_map(out, mission)

    logger.info("Done. LLM calls used: %s / %s", calls_used, mission.max_perplexity_calls)
    plog.step_ok("pipeline", calls_used=calls_used, max_calls=mission.max_perplexity_calls)
    write_pipeline_provenance_json(out)
    build_evidence_bundle(out, mission)
    write_publish_decision(out, mission)
    update_objective_artifacts(out, candidate_action_family="post_pipeline")
    append_research_memory(
        out,
        kind="run_consolidation",
        summary="Run consolidado tras pipeline principal",
        source_artifacts=[
            "run_ledger.json",
            "objective_state.json",
            "publication/publish_decision.json",
        ],
        payload={
            "status": "completed",
            "calls_used": calls_used,
            "max_calls": mission.max_perplexity_calls,
        },
        tags=["run", "consolidation"],
        confidence=0.9,
    )
    update_goal_selection_artifacts(out)
    ledger.upsert_phase("final_decision", "done", meta={"publishable_hint": True})
    ledger.finalize("completed")
    try:
        from paper_pipeline.rag.service import ingest_mission_outputs

        ingest_mission_outputs(out, mission_id)
    except Exception as exc:
        logger.debug("RAG ingest after pipeline skipped: %s", exc)
    return ExitCode.OK
