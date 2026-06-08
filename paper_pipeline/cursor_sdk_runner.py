"""Cursor SDK backend for paper-pipeline (local agent, composer-2.5 default).

Uses ``Agent.create`` / ``Agent.resume`` with streaming into ``cursor_cli.log`` and
persists ``cursor_agent_state.json`` for ``Agent.resume`` across invocations.
"""

from __future__ import annotations

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from paper_pipeline.constants import ExitCode

if TYPE_CHECKING:
    from paper_pipeline.logger import PipelineLogger
    from paper_pipeline.mission import Mission

logger = logging.getLogger(__name__)

CURSOR_AGENT_STATE_JSON = "cursor_agent_state.json"
DEFAULT_CURSOR_MODEL = "composer-2.5"
CURSOR_AGENT_BACKEND_ENV = "CURSOR_AGENT_BACKEND"
CURSOR_AGENT_MODEL_ENV = "CURSOR_AGENT_MODEL"
CURSOR_AGENT_RESUME_ENV = "CURSOR_AGENT_RESUME"


def resolve_cursor_model() -> str:
    return os.environ.get(CURSOR_AGENT_MODEL_ENV, DEFAULT_CURSOR_MODEL).strip() or DEFAULT_CURSOR_MODEL


def resolve_cursor_resume_enabled() -> bool:
    raw = os.environ.get(CURSOR_AGENT_RESUME_ENV, "1").strip().lower()
    return raw not in ("0", "false", "no")


def cursor_sdk_importable() -> bool:
    import sys

    if sys.version_info < (3, 12):
        logger.debug("cursor-sdk requires Python 3.12+ (current %s)", sys.version.split()[0])
        return False
    try:
        import cursor_sdk  # noqa: F401

        return True
    except ImportError:
        return False


def resolve_cursor_backend() -> str:
    raw = os.environ.get(CURSOR_AGENT_BACKEND_ENV, "sdk").strip().lower()
    if raw in ("cli", "subprocess", "agent"):
        return "cli"
    return "sdk"


def _load_agent_state(output_dir: Path, cwd_str: str) -> dict[str, Any] | None:
    path = output_dir / CURSOR_AGENT_STATE_JSON
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Ignoring invalid %s: %s", path, exc)
        return None
    if data.get("cwd") != cwd_str:
        return None
    if not data.get("agent_id"):
        return None
    return data


def _save_agent_state(
    output_dir: Path,
    *,
    agent_id: str,
    cwd_str: str,
    model: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "agent_id": agent_id,
        "backend": "sdk",
        "model": model,
        "cwd": cwd_str,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    (output_dir / CURSOR_AGENT_STATE_JSON).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_sdk_retry_prompt(
    *,
    attempt: int,
    attempts_total: int,
    prev_status: str,
    prev_result: str,
    prev_error: str,
) -> str:
    """Shorter follow-up when the SDK agent already has prior turn context."""

    result_snip = (prev_result or "")[:48_000]
    err_snip = (prev_error or "")[:24_000]
    return (
        f"## Automated retry (attempt {attempt} of {attempts_total})\n\n"
        f"The previous run ended with status **{prev_status}**. "
        "Fix errors, refine `outputs/code/`, or complete missing work. "
        "Do not ask for confirmation; apply changes.\n\n"
        f"### Previous assistant output\n\n```\n{result_snip}\n```\n\n"
        f"### Error detail\n\n```\n{err_snip}\n```\n"
    )


def _is_auth_error(exc: BaseException) -> bool:
    from cursor_sdk.errors import AuthenticationError, PermissionDeniedError

    if isinstance(exc, (AuthenticationError, PermissionDeniedError)):
        return True
    msg = str(exc).lower()
    return "401" in msg or "unauthorized" in msg or "unauthenticated" in msg


def _map_startup_error(exc: BaseException) -> int:
    if _is_auth_error(exc):
        return ExitCode.CURSOR_CLI_AUTH_ERROR
    return ExitCode.ERROR


def _map_run_status(status: str) -> int:
    if status == "finished":
        return ExitCode.OK
    return ExitCode.ERROR


def _cmd_preview(model: str, agent_id: str | None = None) -> list[str]:
    parts = ["cursor-sdk", f"model={model}"]
    if agent_id:
        parts.append(f"agent_id={agent_id}")
    return parts


def _open_agent(
    *,
    api_key: str,
    model: str,
    cwd_str: str,
    output_dir: Path,
    resume_enabled: bool,
):
    from cursor_sdk import Agent, AgentOptions, Client, LocalAgentOptions
    from cursor_sdk.errors import CursorAgentError

    from paper_pipeline.cursor_sdk_bridge_patch import ensure_cursor_sdk_ready

    ensure_cursor_sdk_ready()

    options = AgentOptions(
        api_key=api_key,
        model=model,
        local=LocalAgentOptions(cwd=cwd_str),
    )

    client = Client.launch_bridge(workspace=cwd_str)

    if resume_enabled:
        state = _load_agent_state(output_dir, cwd_str)
        if state and state.get("backend") == "sdk":
            agent_id = str(state["agent_id"])
            try:
                agent = Agent.resume(agent_id, options, client=client)
                logger.info("Cursor SDK resumed agent %s cwd=%s", agent_id, cwd_str)
                return agent, agent_id, True, client
            except CursorAgentError as exc:
                logger.warning("Agent.resume(%s) failed (%s); creating new agent", agent_id, exc)

    agent = Agent.create(options, client=client)
    logger.info("Cursor SDK created agent %s cwd=%s model=%s", agent.agent_id, cwd_str, model)
    return agent, agent.agent_id, False, client


def _run_single_send(
    agent,
    *,
    body: str,
    timeout_sec: float,
    log_path: Path,
    log_append: bool,
    attempt: int,
    attempts_total: int,
    output_dir: Path,
) -> tuple[int, str, str, float, str | None, str]:
    """Execute one ``agent.send`` with streaming and timeout."""

    from cursor_sdk.errors import CursorAgentError

    (output_dir / "cursor_cli_prompt_last.txt").write_text(body, encoding="utf-8")
    logger.info(
        "Cursor SDK attempt %s/%s timeout=%ss prompt_chars=%s",
        attempt,
        attempts_total,
        timeout_sec,
        len(body),
    )

    header = (
        f"\n\n===== sdk attempt {attempt}/{attempts_total} =====\n"
        if log_append
        else f"backend=sdk\nmodel={resolve_cursor_model()}\n"
    )
    if log_append and log_path.is_file():
        log_path.write_text(log_path.read_text(encoding="utf-8") + header, encoding="utf-8")
    else:
        log_path.write_text(header, encoding="utf-8")

    t0 = time.monotonic()
    run_id = ""
    streamed_parts: list[str] = []
    run_holder: dict[str, Any] = {"run": None}

    def _worker():
        nonlocal run_id
        run = agent.send(body)
        run_holder["run"] = run
        run_id = run.id
        for chunk in run.iter_text():
            streamed_parts.append(chunk)
            if chunk:
                with log_path.open("a", encoding="utf-8") as fh:
                    fh.write(chunk)
        return run.wait()

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_worker)
            result = future.result(timeout=timeout_sec)
    except FuturesTimeout:
        dur = time.monotonic() - t0
        active_run = run_holder.get("run")
        if active_run is not None and active_run.supports("cancel"):
            try:
                active_run.cancel()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Cursor SDK cancel after timeout failed: %s", exc)
        logger.error("Cursor SDK timed out after %ss (attempt %s/%s)", timeout_sec, attempt, attempts_total)
        timeout_msg = f"timeout after {timeout_sec}s"
        log_path.open("a", encoding="utf-8").write(f"\n\nTIMEOUT: {timeout_msg}\n")
        return ExitCode.ERROR, "", timeout_msg, dur, run_id or None, agent.agent_id
    except CursorAgentError as exc:
        dur = time.monotonic() - t0
        err = str(exc)
        logger.exception("Cursor SDK startup/send failed")
        return _map_startup_error(exc), "", err, dur, run_id or None, agent.agent_id

    dur = time.monotonic() - t0
    stdout = result.result or "".join(streamed_parts)
    proc_rc = 0 if result.status == "finished" else 1
    footer = (
        f"\n--- run status={result.status} run_id={result.id} "
        f"agent_id={result.agent_id} duration_s={dur:.2f} ---\n"
    )
    log_path.open("a", encoding="utf-8").write(footer)

    code = _map_run_status(str(result.status))
    stderr = "" if code == ExitCode.OK else f"run status={result.status}"
    return code, stdout, stderr, dur, result.id, agent.agent_id


def run_cursor_via_sdk(
    *,
    cwd: Path,
    output_dir: Path,
    base_body: str,
    max_attempts: int,
    timeout_sec: float,
    dry_run: bool,
    api_key: str,
    pipeline_log: PipelineLogger | None = None,
) -> int:
    """Run Cursor via SDK with retries and optional ``Agent.resume``."""

    from paper_pipeline.cursor_cli_runner import (
        CURSOR_DIAGNOSTICS_JSON,
        CURSOR_LOG,
        CURSOR_ROUNDS_JSON,
        _append_cursor_turn,
        _write_cursor_cli_diagnostics_json,
    )

    model = resolve_cursor_model()
    cwd_str = str(cwd.resolve())
    resume_enabled = resolve_cursor_resume_enabled()
    log_path = output_dir / CURSOR_LOG

    if dry_run:
        logger.info(
            "Dry run: would execute Cursor SDK in cwd=%s (up to %s attempts, model=%s)",
            cwd,
            max_attempts,
            model,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"dry_run=true\nbackend=sdk\nmodel={model}\nmax_attempts={max_attempts}\n"
            f"resume={'1' if resume_enabled else '0'}\n"
            f"prompt_chars={len(base_body)}\n",
            encoding="utf-8",
        )
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=len(base_body),
                duration_s=0.0,
                exit_code=0,
                dry_run=True,
                attempt_index=1,
                attempts_total=max_attempts,
                backend="sdk",
                model=model,
            )
        return ExitCode.OK

    cwd.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    agent = None
    sdk_client = None
    agent_id = ""
    rounds_record: list[dict[str, Any]] = []
    last_out, last_err = "", ""
    last_code = ExitCode.ERROR
    last_run_id: str | None = None
    last_cmd = _cmd_preview(model)

    try:
        try:
            agent, agent_id, _resumed, sdk_client = _open_agent(
                api_key=api_key,
                model=model,
                cwd_str=cwd_str,
                output_dir=output_dir,
                resume_enabled=resume_enabled,
            )
        except Exception as exc:
            from cursor_sdk.errors import CursorAgentError

            if sdk_client is not None:
                try:
                    sdk_client.close()
                except Exception:  # noqa: BLE001
                    pass
                sdk_client = None

            if isinstance(exc, CursorAgentError):
                code = _map_startup_error(exc)
                _write_cursor_cli_diagnostics_json(
                    output_dir,
                    cmd=last_cmd,
                    cwd=cwd_str,
                    exit_code=None,
                    stderr=str(exc),
                    stdout="",
                    timed_out=False,
                    error=str(exc),
                    backend="sdk",
                    model=model,
                )
                return code
            raise
        last_cmd = _cmd_preview(model, agent_id)

        prev_status = "error"
        for attempt in range(1, max_attempts + 1):
            if attempt == 1:
                body = base_body
            else:
                body = build_sdk_retry_prompt(
                    attempt=attempt,
                    attempts_total=max_attempts,
                    prev_status=prev_status,
                    prev_result=last_out,
                    prev_error=last_err,
                )

            code, last_out, last_err, dur, run_id, current_agent_id = _run_single_send(
                agent,
                body=body,
                timeout_sec=timeout_sec,
                log_path=log_path,
                log_append=attempt > 1,
                attempt=attempt,
                attempts_total=max_attempts,
                output_dir=output_dir,
            )
            agent_id = current_agent_id
            last_run_id = run_id
            proc_rc = 0 if code == ExitCode.OK else 1
            prev_status = "finished" if code == ExitCode.OK else "error"

            _append_cursor_turn(
                output_dir,
                exit_code=proc_rc,
                stdout=last_out,
                stderr=last_err,
                attempt=attempt,
                attempts_total=max_attempts,
                backend="sdk",
                run_id=run_id,
                agent_id=agent_id,
            )

            rounds_record.append(
                {
                    "attempt": attempt,
                    "process_returncode": proc_rc,
                    "pipeline_exit_kind": code,
                    "backend": "sdk",
                    "run_id": run_id,
                    "agent_id": agent_id,
                    "model": model,
                }
            )

            if pipeline_log is not None:
                pipeline_log.cursor_cli_subprocess_done(
                    cwd=cwd_str,
                    prompt_chars=len(body),
                    duration_s=dur,
                    exit_code=proc_rc,
                    attempt_index=attempt,
                    attempts_total=max_attempts,
                    backend="sdk",
                    run_id=run_id,
                    agent_id=agent_id,
                    model=model,
                )

            if code == ExitCode.OK:
                _save_agent_state(output_dir, agent_id=agent_id, cwd_str=cwd_str, model=model)
                _write_cursor_cli_diagnostics_json(
                    output_dir,
                    cmd=last_cmd,
                    cwd=cwd_str,
                    exit_code=0,
                    stderr=last_err,
                    stdout=last_out,
                    timed_out=False,
                    backend="sdk",
                    model=model,
                    agent_id=agent_id,
                    run_id=run_id,
                    iteration={
                        "max_attempts": max_attempts,
                        "stopped_after_attempt": attempt,
                        "reason": "success",
                        "rounds": rounds_record,
                    },
                )
                (output_dir / CURSOR_ROUNDS_JSON).write_text(
                    json.dumps(rounds_record, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                logger.info("Cursor SDK diagnostics: %s", output_dir / CURSOR_DIAGNOSTICS_JSON)
                return ExitCode.OK

            if code == ExitCode.CURSOR_CLI_AUTH_ERROR:
                (output_dir / CURSOR_ROUNDS_JSON).write_text(
                    json.dumps(rounds_record, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                return code

            last_code = code
            if attempt < max_attempts:
                logger.warning(
                    "Cursor SDK attempt %s/%s failed (code=%s); retrying",
                    attempt,
                    max_attempts,
                    code,
                )
                continue

        (output_dir / CURSOR_ROUNDS_JSON).write_text(
            json.dumps(rounds_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=last_cmd,
            cwd=cwd_str,
            exit_code=1,
            stderr=last_err,
            stdout=last_out,
            timed_out=False,
            backend="sdk",
            model=model,
            agent_id=agent_id,
            run_id=last_run_id,
            iteration={
                "max_attempts": max_attempts,
                "stopped_after_attempt": max_attempts,
                "reason": "exhausted",
                "rounds": rounds_record,
            },
        )
        logger.error("Cursor SDK: all %s attempts failed (last code=%s)", max_attempts, last_code)
        return last_code
    finally:
        if agent is not None:
            try:
                agent.close()
            except Exception as exc:  # noqa: BLE001 — best-effort cleanup
                logger.warning("Cursor SDK agent.close() failed: %s", exc)
        if sdk_client is not None:
            try:
                sdk_client.close()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Cursor SDK client.close() failed: %s", exc)
