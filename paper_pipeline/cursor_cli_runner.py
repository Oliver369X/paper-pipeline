"""Run Cursor CLI (`agent -p --force` + optional `CURSOR_AGENT_EXTRA_ARGS`) headless; append to outputs/cursor_turn.md.

Varios intentos por run (reintentos con contexto): ``debugging.cursor_max_attempts`` en ``mission.md`` o
``CURSOR_CLI_MAX_ROUNDS`` en el entorno. Tras un fallo, el siguiente prompt incluye la salida del intento
anterior para que el agente codificador pueda corregir o iterar. El primer intento con exit 0 termina el bucle.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any
import shlex
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from paper_pipeline.constants import CURSOR_AGENT_VERSION_EXPECTED_ENV, ExitCode
from paper_pipeline.integration_transcript import append_transcript
from paper_pipeline.mission import Mission

logger = logging.getLogger(__name__)

CURSOR_LOG = "cursor_cli.log"
CURSOR_DIAGNOSTICS_JSON = "cursor_cli_diagnostics.json"
CURSOR_ROUNDS_JSON = "cursor_cli_rounds.json"
# Windows: el prompt como último argv puede superar el límite de línea de comandos (~8191 en cmd).
_DEFAULT_WIN_MAX_ARG_CHARS = 6000
_MAX_FOLLOWUP_STDOUT = 48_000
_MAX_FOLLOWUP_STDERR = 24_000


def _use_stdin_for_prompt(body: str) -> bool:
    """Evita CreateProcess «La línea de comandos es demasiado larga» en Windows."""

    flag = os.environ.get("CURSOR_CLI_PROMPT_STDIN", "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True
    if flag in ("0", "false", "no"):
        return False
    if os.name != "nt":
        return False
    try:
        limit = int(os.environ.get("CURSOR_CLI_WIN_MAX_ARG_CHARS", str(_DEFAULT_WIN_MAX_ARG_CHARS)))
    except ValueError:
        limit = _DEFAULT_WIN_MAX_ARG_CHARS
    return len(body) > limit


def _write_cursor_cli_diagnostics_json(
    output_dir: Path,
    *,
    cmd: list[str],
    cwd: str,
    exit_code: int | None,
    stderr: str,
    stdout: str,
    timed_out: bool,
    error: str | None = None,
    iteration: dict[str, Any] | None = None,
) -> None:
    """Persistencia legible para la UI: comando, stderr, pistas de recuperación."""

    output_dir.mkdir(parents=True, exist_ok=True)
    hints: list[str] = []
    combined = (stderr or "") + (stdout or "")
    if exit_code not in (None, 0) or error:
        hints.append("Revisá `outputs/cursor_cli.log` y variables CURSOR_AGENT_BIN, CURSOR_API_KEY")
        if "401" in combined or "Unauthorized" in combined:
            hints.append("CURSOR_API_KEY inválida o sin permisos")
        if "not found" in combined.lower() or "No such file" in combined:
            hints.append("Definí CURSOR_AGENT_BIN con ruta absoluta al ejecutable (Windows: where agent)")
    payload: dict[str, Any] = {
        "command_preview": cmd[:16],
        "cwd": cwd,
        "exit_code": exit_code,
        "stderr_truncated": (stderr or "")[:8000],
        "stdout_truncated": (stdout or "")[:4000],
        "timed_out": timed_out,
        "error": error,
        "remediation_hints": hints,
    }
    if iteration:
        payload["iteration"] = iteration
    (output_dir / CURSOR_DIAGNOSTICS_JSON).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _resolve_agent_executable(agent_bin: str) -> Path | None:
    """Ruta absoluta al ejecutable. Hay que usar la ruta que devuelve `which`, no solo el nombre corto (p. ej. `agent`), sobre todo en Windows."""
    raw = Path(agent_bin)
    if raw.is_file():
        return raw.resolve()
    found = shutil.which(agent_bin)
    if not found:
        return None
    # No exigimos is_file() aquí: en tests se mockea `which` sin crear el binario en disco.
    return Path(found).resolve()
DEFAULT_CURSOR_TURN = "cursor_turn.md"
_MAX_FILE_SNIP = 80_000
_MAX_NEXT = 40_000


def _read_if_exists(path: Path, limit: int) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) > limit:
        return text[:limit] + "\n\n[truncated]\n"
    return text


def build_cursor_prompt(
    output_dir: Path,
    mission: Mission | None = None,
    *,
    extra_paths: list[Path] | None = None,
) -> str:
    """Assemble prompt from methodology, experiments, optional next_instruction, quality_gaps."""

    lines: list[str] = [
        "You are working in a research paper pipeline repository. Follow .cursorrules if present.",
        "Place runnable code under outputs/code/. Keep dependencies minimal; add requirements.txt if needed.",
        "",
    ]
    if mission is not None:
        lines.extend(
            [
                f"Topic: {mission.topic}",
                f"Target venue: {mission.paper_target}",
                "",
            ]
        )

    next_p = output_dir / "next_instruction.md"
    if next_p.is_file():
        lines.append("--- Priority: follow next_instruction.md first ---")
        lines.append(_read_if_exists(next_p, _MAX_NEXT))
        lines.append("--- End next_instruction.md ---\n")

    for name in ("methodology.md", "experiments.md", "gaps.md", "sota.md"):
        p = output_dir / name
        if p.is_file():
            lines.append(f"## File: {name}\n")
            lines.append(_read_if_exists(p, _MAX_FILE_SNIP))
            lines.append("")

    q = output_dir / "quality_gaps.md"
    if q.is_file():
        lines.append("## quality_gaps.md (optional context)\n")
        lines.append(_read_if_exists(q, 40_000))
        lines.append("")

    if extra_paths:
        for ep in extra_paths:
            if ep.is_file():
                lines.append(f"## {ep.name}\n")
                lines.append(_read_if_exists(ep, _MAX_FILE_SNIP))
                lines.append("")

    lines.append(
        "Implement or refine code under outputs/code/ as appropriate. "
        "Do not ask for confirmation; apply changes. Summarize what you did at the end."
    )
    return "\n".join(lines)


def _resolve_max_attempts(mission: Mission | None) -> int:
    """Prioridad: ``CURSOR_CLI_MAX_ROUNDS`` (env) > ``mission.debugging.cursor_max_attempts`` > 1 si no hay misión."""

    raw = os.environ.get("CURSOR_CLI_MAX_ROUNDS", "").strip()
    if raw:
        try:
            return max(1, min(20, int(raw)))
        except ValueError:
            logger.warning("CURSOR_CLI_MAX_ROUNDS invalid (%r); using mission/default", raw)
    if mission is not None:
        return max(1, min(20, mission.debugging.cursor_max_attempts))
    return 1


def build_followup_cursor_prompt(
    base_prompt: str,
    *,
    attempt: int,
    attempts_total: int,
    prev_exit_code: int,
    prev_stdout: str,
    prev_stderr: str,
) -> str:
    """Segundo y siguientes intentos: contexto del fallo anterior + la misma tarea base."""

    out_snip = prev_stdout[:_MAX_FOLLOWUP_STDOUT] if prev_stdout else ""
    err_snip = prev_stderr[:_MAX_FOLLOWUP_STDERR] if prev_stderr else ""
    if len(prev_stdout) > len(out_snip):
        out_snip += "\n\n[stdout truncated]\n"
    if len(prev_stderr) > len(err_snip):
        err_snip += "\n\n[stderr truncated]\n"

    return (
        f"## Automated Cursor CLI follow-up (attempt {attempt} of {attempts_total})\n\n"
        f"The previous `agent` invocation exited with code **{prev_exit_code}**. "
        "Use the output below to fix errors, refine `outputs/code/`, or complete missing work. "
        "Do not ask for confirmation; apply changes.\n\n"
        f"### Previous stdout\n\n```\n{out_snip}\n```\n\n"
        f"### Previous stderr\n\n```\n{err_snip}\n```\n\n"
        "---\n\n"
        "## Original task (full context)\n\n"
        f"{base_prompt}"
    )


def _append_cursor_turn(
    output_dir: Path,
    *,
    exit_code: int,
    stdout: str,
    stderr: str,
    attempt: int | None = None,
    attempts_total: int | None = None,
) -> None:
    path = output_dir / DEFAULT_CURSOR_TURN
    stamp = datetime.now(UTC).isoformat()
    out_snip = stdout[:40_000] if stdout else ""
    err_snip = stderr[:20_000] if stderr else ""
    att = ""
    if attempt is not None and attempts_total is not None:
        att = f" attempt {attempt}/{attempts_total}"
    block = (
        f"\n\n---\n## Cursor CLI (automated){att} {stamp}\n"
        f"exit_code={exit_code}\n\n"
        f"### stdout\n```\n{out_snip}\n```\n\n"
        f"### stderr\n```\n{err_snip}\n```\n"
    )
    if path.is_file():
        path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")
    else:
        path.write_text(block.lstrip("\n"), encoding="utf-8")

    extra = os.environ.get("CURSOR_AGENT_EXTRA_ARGS", "").strip()
    meta_lines = [
        f"exit_code={exit_code}",
        f"CURSOR_AGENT_EXTRA_ARGS={extra or '—'}",
    ]
    if attempt is not None and attempts_total is not None:
        meta_lines.append(f"attempt={attempt}/{attempts_total}")
    append_transcript(
        output_dir,
        source="cursor_cli",
        heading="Cursor CLI (agent headless)",
        body=(
            f"```\n{out_snip}\n```\n\n### stderr\n\n```\n{err_snip}\n```\n"
            if (out_snip or err_snip)
            else "(sin salida capturada)"
        ),
        meta_lines=meta_lines,
    )


def _log_agent_version(agent_bin: str, pipeline_log: "PipelineLogger | None") -> None:
    if pipeline_log is None:
        return
    try:
        proc = subprocess.run(
            [agent_bin, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        ver = (proc.stdout or proc.stderr or "").strip()[:500]
        expected = os.environ.get(CURSOR_AGENT_VERSION_EXPECTED_ENV, "").strip()
        mismatch = bool(expected and expected not in ver and ver not in expected)
        pipeline_log.cursor_version_line(agent_bin=agent_bin, version_text=ver or "(empty)", mismatch=mismatch)
        if mismatch:
            logger.warning(
                "Cursor CLI version may not match expected (%s). Got: %s",
                expected,
                ver[:200],
            )
    except OSError as exc:
        pipeline_log.step_error("cursor_version_check", error="agent_version_failed", detail=str(exc))


def _run_single_cursor_invocation(
    *,
    body: str,
    cwd_str: str,
    output_dir: Path,
    agent_exe: Path,
    extra_parts: list[str],
    timeout_sec: float,
    env: dict[str, str],
    pipeline_log: "PipelineLogger | None",
    attempt: int,
    attempts_total: int,
    log_append: bool,
) -> tuple[int, str, str, float, list[str], int | None]:
    """Una pasada ``agent -p --force``.

    Devuelve (ExitCode, stdout, stderr, duration_s, cmd, process_returncode).
    ``process_returncode`` es ``None`` si no hubo proceso (timeout / spawn error).
    """

    prompt_via_stdin = _use_stdin_for_prompt(body)
    cmd: list[str] = [
        str(agent_exe),
        "-p",
        "--force",
        "--output-format",
        "text",
        *extra_parts,
    ]
    if not prompt_via_stdin:
        cmd.append(body)

    log_path = output_dir / CURSOR_LOG
    prompt_len = len(body)

    if prompt_via_stdin:
        logger.info(
            "Cursor CLI (%s) attempt %s/%s cwd=%s timeout=%ss; prompt por stdin (%s chars)",
            agent_exe,
            attempt,
            attempts_total,
            cwd_str,
            timeout_sec,
            prompt_len,
        )
        (output_dir / "cursor_cli_prompt_last.txt").write_text(body, encoding="utf-8")
    else:
        logger.info(
            "Cursor CLI (%s) attempt %s/%s cwd=%s timeout=%ss",
            agent_exe,
            attempt,
            attempts_total,
            cwd_str,
            timeout_sec,
        )

    t0 = time.monotonic()
    try:
        run_kw: dict[str, Any] = {
            "cwd": cwd_str,
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": timeout_sec,
            "env": env,
        }
        if prompt_via_stdin:
            run_kw["input"] = body
        proc = subprocess.run(cmd, **run_kw)
    except subprocess.TimeoutExpired:
        dur = time.monotonic() - t0
        logger.exception("Cursor CLI timed out after %ss", timeout_sec)
        block = f"\n\n===== attempt {attempt}/{attempts_total} TIMEOUT after {timeout_sec}s =====\n\n"
        if log_append and log_path.is_file():
            log_path.write_text(log_path.read_text(encoding="utf-8") + block, encoding="utf-8")
        else:
            log_path.write_text(f"timeout after {timeout_sec}s\n{block}", encoding="utf-8")
        _append_cursor_turn(
            output_dir,
            exit_code=-1,
            stdout="",
            stderr="timeout",
            attempt=attempt,
            attempts_total=attempts_total,
        )
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=cmd,
            cwd=cwd_str,
            exit_code=-1,
            stderr="timeout",
            stdout="",
            timed_out=True,
            error=f"timeout after {timeout_sec}s",
            iteration={"attempt": attempt, "attempts_total": attempts_total, "phase": "timeout"},
        )
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=prompt_len,
                duration_s=dur,
                exit_code=None,
                timed_out=True,
                attempt_index=attempt,
                attempts_total=attempts_total,
            )
        return ExitCode.ERROR, "", "", dur, cmd, None
    except FileNotFoundError as exc:
        dur = time.monotonic() - t0
        logger.exception(
            "No se pudo ejecutar el binario del Cursor CLI (%s). "
            "En Windows probá CURSOR_AGENT_BIN con ruta absoluta al agent.exe.",
            agent_exe,
        )
        msg = (
            f"{exc!s}\n\n"
            "Sugerencia: `where agent` en CMD y copiá la ruta completa a CURSOR_AGENT_BIN en .env\n"
        )
        if log_append and log_path.is_file():
            log_path.write_text(log_path.read_text(encoding="utf-8") + f"\n===== attempt {attempt}/{attempts_total} =====\n" + msg, encoding="utf-8")
        else:
            log_path.write_text(msg, encoding="utf-8")
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=cmd,
            cwd=cwd_str,
            exit_code=None,
            stderr=str(exc),
            stdout="",
            timed_out=False,
            error=f"FileNotFoundError: {exc}",
        )
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=prompt_len,
                duration_s=dur,
                exit_code=None,
                error=f"FileNotFoundError: {exc}",
                attempt_index=attempt,
                attempts_total=attempts_total,
            )
        return ExitCode.CURSOR_CLI_NOT_FOUND, "", "", dur, cmd, None
    except OSError as exc:
        dur = time.monotonic() - t0
        logger.exception("Failed to spawn Cursor CLI")
        if log_append and log_path.is_file():
            log_path.write_text(
                log_path.read_text(encoding="utf-8") + f"\n===== attempt {attempt}/{attempts_total} =====\n{exc}\n",
                encoding="utf-8",
            )
        else:
            log_path.write_text(str(exc), encoding="utf-8")
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=cmd,
            cwd=cwd_str,
            exit_code=None,
            stderr=str(exc),
            stdout="",
            timed_out=False,
            error=f"OSError: {exc}",
        )
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=prompt_len,
                duration_s=dur,
                exit_code=None,
                error=f"OSError: {exc}",
                attempt_index=attempt,
                attempts_total=attempts_total,
            )
        return ExitCode.ERROR, "", "", dur, cmd, None

    dur = time.monotonic() - t0
    out = proc.stdout or ""
    err = proc.stderr or ""
    chunk = (
        f"\n\n===== attempt {attempt}/{attempts_total} exit={proc.returncode} =====\n"
        f"--- stdout ---\n{out}\n--- stderr ---\n{err}\n"
    )
    if log_append and log_path.is_file():
        log_path.write_text(log_path.read_text(encoding="utf-8") + chunk, encoding="utf-8")
    else:
        log_path.write_text(
            f"exit={proc.returncode}\n--- stdout ---\n{out}\n--- stderr ---\n{err}\n",
            encoding="utf-8",
        )
    _append_cursor_turn(
        output_dir,
        exit_code=proc.returncode,
        stdout=out,
        stderr=err,
        attempt=attempt,
        attempts_total=attempts_total,
    )
    _write_cursor_cli_diagnostics_json(
        output_dir,
        cmd=cmd,
        cwd=cwd_str,
        exit_code=proc.returncode,
        stderr=err,
        stdout=out,
        timed_out=False,
        iteration={"attempt": attempt, "attempts_total": attempts_total, "phase": "completed"},
    )

    if proc.returncode != 0:
        logger.error("Cursor CLI exited with code %s (attempt %s/%s)", proc.returncode, attempt, attempts_total)
        combined = err + out
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=prompt_len,
                duration_s=dur,
                exit_code=proc.returncode,
                attempt_index=attempt,
                attempts_total=attempts_total,
            )
        if "401" in combined or "Unauthorized" in combined:
            return ExitCode.CURSOR_CLI_AUTH_ERROR, out, err, dur, cmd, proc.returncode
        return ExitCode.ERROR, out, err, dur, cmd, proc.returncode

    logger.info("Cursor CLI finished successfully (attempt %s/%s)", attempt, attempts_total)
    if pipeline_log is not None:
        pipeline_log.cursor_cli_subprocess_done(
            cwd=cwd_str,
            prompt_chars=prompt_len,
            duration_s=dur,
            exit_code=proc.returncode,
            attempt_index=attempt,
            attempts_total=attempts_total,
        )
    return ExitCode.OK, out, err, dur, cmd, proc.returncode


def run_cursor_cli(
    *,
    cwd: Path,
    output_dir: Path,
    mission: Mission | None = None,
    prompt: str | None = None,
    prompt_file: Path | None = None,
    dry_run: bool = False,
    pipeline_log: "PipelineLogger | None" = None,
) -> int:
    """Invoca ``agent -p --force`` hasta ``debugging.cursor_max_attempts`` veces; para en el primer éxito."""

    api_key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        logger.error("CURSOR_API_KEY is not set")
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=["(cursor_cli not started)"],
            cwd=str(cwd.resolve()),
            exit_code=None,
            stderr="",
            stdout="",
            timed_out=False,
            error="CURSOR_API_KEY is not set",
        )
        return ExitCode.CURSOR_CLI_AUTH_ERROR

    agent_bin = os.environ.get("CURSOR_AGENT_BIN", "agent").strip() or "agent"
    agent_exe = _resolve_agent_executable(agent_bin)
    if agent_exe is None:
        logger.error(
            "Cursor CLI not found (%r). Instalá el CLI headless y asegurate de que "
            "`agent` esté en PATH, o definí CURSOR_AGENT_BIN con la ruta absoluta al .exe "
            "(Windows). Docs: https://cursor.com/docs/cli/headless",
            agent_bin,
        )
        _write_cursor_cli_diagnostics_json(
            output_dir,
            cmd=[agent_bin, "(not found)"],
            cwd=str(cwd.resolve()),
            exit_code=None,
            stderr="",
            stdout="",
            timed_out=False,
            error="Cursor CLI executable not found",
        )
        return ExitCode.CURSOR_CLI_NOT_FOUND

    if prompt_file is not None and prompt_file.is_file():
        base_body = prompt_file.read_text(encoding="utf-8")
    elif prompt is not None:
        base_body = prompt
    else:
        base_body = build_cursor_prompt(output_dir, mission)

    max_attempts = _resolve_max_attempts(mission)
    timeout_sec = float(os.environ.get("CURSOR_CLI_TIMEOUT_SEC", "1800"))

    extra = os.environ.get("CURSOR_AGENT_EXTRA_ARGS", "").strip()
    extra_parts: list[str] = shlex.split(extra) if extra else []

    cwd_str = str(cwd.resolve())
    log_path = output_dir / CURSOR_LOG

    # Dry-run: un solo bloque con el primer prompt (misma forma que antes).
    probe = base_body
    pv_stdin = _use_stdin_for_prompt(probe)
    cmd0: list[str] = [
        str(agent_exe),
        "-p",
        "--force",
        "--output-format",
        "text",
        *extra_parts,
    ]
    if not pv_stdin:
        cmd0.append(probe)

    if dry_run:
        logger.info("Dry run: would execute %s in cwd=%s (up to %s attempts)", agent_exe, cwd, max_attempts)
        logger.info(
            "Prompt length: %s chars (%s)",
            len(probe),
            "stdin" if pv_stdin else "argv",
        )
        log_path.write_text(
            f"dry_run=true\nmax_attempts={max_attempts}\n"
            f"prompt_delivery={'stdin' if pv_stdin else 'argv'}\n"
            f"command={cmd0[:8]!r} ... [prompt omitted]\n",
            encoding="utf-8",
        )
        if pipeline_log is not None:
            pipeline_log.cursor_cli_subprocess_done(
                cwd=cwd_str,
                prompt_chars=len(probe),
                duration_s=0.0,
                exit_code=0,
                dry_run=True,
                attempt_index=1,
                attempts_total=max_attempts,
            )
        return ExitCode.OK

    _log_agent_version(str(agent_exe), pipeline_log)

    cwd.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    env = {
        **os.environ,
        "CURSOR_API_KEY": api_key,
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }

    rounds_record: list[dict[str, Any]] = []
    last_out, last_err = "", ""
    last_code = ExitCode.ERROR
    last_cmd: list[str] = [str(agent_exe), "-p", "--force", "--output-format", "text"]
    prev_proc_exit: int = -1

    for attempt in range(1, max_attempts + 1):
        if attempt == 1:
            body = base_body
        else:
            body = build_followup_cursor_prompt(
                base_body,
                attempt=attempt,
                attempts_total=max_attempts,
                prev_exit_code=prev_proc_exit,
                prev_stdout=last_out,
                prev_stderr=last_err,
            )

        log_append = attempt > 1
        code, last_out, last_err, _dur, last_cmd, proc_rc = _run_single_cursor_invocation(
            body=body,
            cwd_str=cwd_str,
            output_dir=output_dir,
            agent_exe=agent_exe,
            extra_parts=extra_parts,
            timeout_sec=timeout_sec,
            env=env,
            pipeline_log=pipeline_log,
            attempt=attempt,
            attempts_total=max_attempts,
            log_append=log_append,
        )
        rounds_record.append(
            {
                "attempt": attempt,
                "process_returncode": proc_rc,
                "pipeline_exit_kind": code,
            }
        )

        if code == ExitCode.OK:
            _write_cursor_cli_diagnostics_json(
                output_dir,
                cmd=last_cmd,
                cwd=cwd_str,
                exit_code=0,
                stderr=last_err,
                stdout=last_out,
                timed_out=False,
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
            logger.info("Cursor CLI diagnostics: %s", output_dir / CURSOR_DIAGNOSTICS_JSON)
            return ExitCode.OK

        if code in (ExitCode.CURSOR_CLI_NOT_FOUND, ExitCode.CURSOR_CLI_AUTH_ERROR):
            (output_dir / CURSOR_ROUNDS_JSON).write_text(
                json.dumps(rounds_record, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return code

        prev_proc_exit = proc_rc if proc_rc is not None else -1
        last_code = code
        if attempt < max_attempts:
            logger.warning(
                "Cursor CLI attempt %s/%s failed (code=%s); retrying with follow-up prompt",
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
        exit_code=prev_proc_exit if prev_proc_exit is not None else 1,
        stderr=last_err,
        stdout=last_out,
        timed_out=False,
        iteration={
            "max_attempts": max_attempts,
            "stopped_after_attempt": max_attempts,
            "reason": "exhausted",
            "rounds": rounds_record,
        },
    )
    logger.error("Cursor CLI: all %s attempts failed (last pipeline code=%s)", max_attempts, last_code)
    return last_code
