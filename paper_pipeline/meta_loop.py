"""Meta-agent loop: Perplexity reviews Cursor output and writes the next instruction (bounded, safe)."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from perplexity_webui_scraper import ClientConfig, ConversationConfig, Perplexity
from perplexity_webui_scraper.models import MODELS

from paper_pipeline.integration_transcript import append_transcript

logger = logging.getLogger(__name__)

STATE_NAME = "meta_loop_state.json"
DEFAULT_CURSOR_TURN = "cursor_turn.md"
DEFAULT_NEXT = "next_instruction.md"
DEFAULT_LOG = "meta_loop_log.md"
META_AUDIT = "perplexity_meta_audit.md"


def _strip_continue_prefix(text: str) -> str:
    """Remove leading CONTINUE line and following blank lines (Perplexity meta output)."""

    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip().upper().startswith("CONTINUE"):
        i = 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
    return "\n".join(lines[i:]).strip()


def _meta_prompt(*, goal: str, cursor_output: str, round_num: int, max_rounds: int) -> str:
    return f"""Eres un director técnico que supervisa un agente de programación (Cursor).

Objetivo global del usuario (resumen):
{goal}

--- Output reciente del agente Cursor (ronda {round_num} de máximo {max_rounds}) ---
{cursor_output}
--- Fin del output ---

Instrucciones:
1. Si la tarea ya está completa respecto al objetivo, o hay riesgo claro (borrar datos, credenciales, bucles peligrosos), responde SOLO con la palabra STOP en la primera línea, luego una línea vacía, luego una frase breve del motivo.
2. Si debe continuar, primera línea CONTINUE, luego línea vacía, luego instrucciones concretas en Markdown para el siguiente paso (qué archivos tocar, qué verificar). Sé breve.

Idioma: español."""


def run_meta_loop(
    output_dir: Path | str = "outputs",
    *,
    cursor_turn_file: str = DEFAULT_CURSOR_TURN,
    goal: str = "Completar el paper pipeline: código bajo outputs/code/ alineado con methodology y experiments.",
    model: str = "claude-sonnet-4.6-thinking",
    language: str = "es-ES",
) -> int:
    """Run one meta-agent round. Returns 0=continue, 1=stop or error, 2=skip (no input file)."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    turn_path = out / cursor_turn_file
    if not turn_path.is_file() or not turn_path.read_text(encoding="utf-8").strip():
        logger.warning("No hay contenido en %s — pega ahí el output de Cursor y vuelve a ejecutar.", turn_path)
        return 2

    max_rounds = int(os.environ.get("META_MAX_ROUNDS", "12"))
    state_path = out / STATE_NAME
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        round_num = int(state.get("round", 0)) + 1
    else:
        state = {}
        round_num = 1

    if round_num > max_rounds:
        logger.warning("Límite META_MAX_ROUNDS=%s alcanzado (seguridad). No se llama a Perplexity.", max_rounds)
        _write_stop_files(out, round_num, max_rounds, "Límite de rondas alcanzado (META_MAX_ROUNDS).")
        return 1

    token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    if not token:
        logger.error("PERPLEXITY_SESSION_TOKEN no está definido.")
        return 1

    if model not in MODELS:
        logger.error("Modelo desconocido: %s", model)
        return 1

    cursor_output = turn_path.read_text(encoding="utf-8")
    if len(cursor_output) > 100_000:
        cursor_output = cursor_output[:100_000] + "\n\n[truncado para meta-loop]\n"

    prompt = _meta_prompt(
        goal=goal,
        cursor_output=cursor_output,
        round_num=round_num,
        max_rounds=max_rounds,
    )

    cfg = ConversationConfig(
        model=model,
        citation_mode="clean",
        language=language,
        save_to_library=True,
    )
    client = Perplexity(token, config=ClientConfig())

    resume_uuid = (state.get("perplexity_backend_uuid") or "").strip() or None
    resume_rw = state.get("perplexity_read_write_token")

    try:
        if resume_uuid:
            logger.info(
                "Meta-loop resume Perplexity thread uuid=%s…",
                resume_uuid[:8],
            )
            conv = client.resume_conversation(
                cfg,
                backend_uuid=resume_uuid,
                read_write_token=resume_rw if isinstance(resume_rw, str) else None,
            )
        else:
            conv = client.create_conversation(cfg)
        conv.ask(prompt)
        answer = (conv.answer or "").strip()
        _uid = getattr(conv, "uuid", None)
        _rw = getattr(conv, "read_write_token", None)
        if _uid:
            logger.info(
                "Perplexity thread backend_uuid=%s (session token account; check Library on perplexity.ai)",
                _uid,
            )
    except Exception:
        logger.exception("Fallo llamando a Perplexity")
        return 1
    finally:
        client.close()

    first_line = answer.splitlines()[0].strip().upper() if answer else ""
    is_stop = first_line.startswith("STOP") or "STOP" in first_line[:20]

    next_path = out / DEFAULT_NEXT
    log_path = out / DEFAULT_LOG

    hdr = f"<!-- meta_loop round={round_num} {datetime.now(UTC).isoformat()} -->\n\n"
    if is_stop:
        next_body = hdr + answer + "\n"
    else:
        # paper-loop solo ejecuta Cursor si hay bloque @CURSOR en markdown
        instr = _strip_continue_prefix(answer) if answer else ""
        next_body = hdr + "@CURSOR\n\n" + instr + "\n"
    next_path.write_text(next_body, encoding="utf-8")

    audit_path = out / META_AUDIT
    audit_line = (
        f"## Ronda {round_num} — {datetime.now(UTC).isoformat()}Z\n"
        f"- decision: {'STOP' if is_stop else 'CONTINUE'}\n"
        f"- backend_uuid: {_uid or '(none)'}\n\n"
    )
    if audit_path.is_file():
        audit_path.write_text(audit_path.read_text(encoding="utf-8") + audit_line, encoding="utf-8")
    else:
        audit_path.write_text("# Perplexity meta-loop (auditoría)\n\n" + audit_line, encoding="utf-8")

    append_transcript(
        out,
        source="perplexity_meta_loop",
        heading=f"Perplexity (meta-loop) — ronda {round_num}",
        body=answer or "(sin texto)",
        meta_lines=[
            f"modelo={model}",
            f"decisión={'STOP' if is_stop else 'CONTINUE'}",
            f"backend_uuid={_uid or '—'}",
        ],
    )

    log_line = (
        f"- {datetime.now(UTC).isoformat()}Z ronda={round_num}/{max_rounds} "
        f"decision={'STOP' if is_stop else 'CONTINUE'}\n"
    )
    if log_path.is_file():
        log_path.write_text(log_path.read_text(encoding="utf-8") + log_line, encoding="utf-8")
    else:
        log_path.write_text("# Meta loop log\n\n" + log_line, encoding="utf-8")

    state_out: dict = {
        "round": round_num,
        "max_rounds": max_rounds,
        "last_decision": "STOP" if is_stop else "CONTINUE",
        "updated": datetime.now(UTC).isoformat() + "Z",
    }
    if _uid:
        state_out["perplexity_backend_uuid"] = _uid
    if _rw:
        state_out["perplexity_read_write_token"] = _rw
    state_path.write_text(json.dumps(state_out, indent=2), encoding="utf-8")

    logger.info("Escrito %s (ronda %s)", next_path, round_num)
    return 1 if is_stop else 0


def _write_stop_files(out: Path, round_num: int, max_rounds: int, reason: str) -> None:
    next_path = out / DEFAULT_NEXT
    next_path.write_text(
        f"<!-- meta_loop STOP -->\n\nSTOP\n\n{reason}\n",
        encoding="utf-8",
    )
    log_path = out / DEFAULT_LOG
    log_line = f"- {datetime.now(UTC).isoformat()}Z ronda={round_num}/{max_rounds} decision=STOP reason=limit\n"
    if log_path.is_file():
        log_path.write_text(log_path.read_text(encoding="utf-8") + log_line, encoding="utf-8")
    else:
        log_path.write_text("# Meta loop log\n\n" + log_line, encoding="utf-8")
