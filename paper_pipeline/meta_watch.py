"""Watch outputs/cursor_turn.md and run meta-loop when it stabilizes after edits (stdlib only)."""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from paper_pipeline.meta_loop import DEFAULT_CURSOR_TURN, DEFAULT_NEXT, run_meta_loop

logger = logging.getLogger(__name__)

_DEFAULT_GOAL = (
    "Completar el paper pipeline: código bajo outputs/code/ alineado con methodology y experiments."
)


def _is_stop_instruction(out: Path) -> bool:
    path = out / DEFAULT_NEXT
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        return stripped.upper().startswith("STOP")
    return False


def watch_cursor_turn(
    output_dir: Path | str = "outputs",
    *,
    goal: str = _DEFAULT_GOAL,
    model: str = "best",
    cursor_turn_file: str = DEFAULT_CURSOR_TURN,
) -> None:
    """Poll cursor_turn file; after debounce, run Perplexity reviewer. Loop until KeyboardInterrupt."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    out = Path(output_dir)
    turn_path = out / cursor_turn_file

    poll_s = float(os.environ.get("META_WATCH_POLL", "2"))
    debounce_s = float(os.environ.get("META_WATCH_DEBOUNCE", "1.5"))
    exit_on_stop = os.environ.get("META_WATCH_EXIT_ON_STOP", "").lower() in ("1", "true", "yes")

    last_executed_mtime: float | None = None
    pending: tuple[float, float] | None = None

    logger.info(
        "paper-meta-watch: vigilando %s (poll=%ss debounce=%ss exit_on_stop=%s)",
        turn_path.resolve(),
        poll_s,
        debounce_s,
        exit_on_stop,
    )
    logger.info("Ctrl+C para detener.")

    try:
        while True:
            time.sleep(poll_s)
            if not turn_path.is_file():
                pending = None
                continue

            mt = turn_path.stat().st_mtime
            if last_executed_mtime is not None and mt == last_executed_mtime:
                pending = None
                continue

            now = time.monotonic()
            if pending is None or pending[0] != mt:
                pending = (mt, now)
                logger.debug("Cambio detectado mtime=%s, esperando debounce...", mt)
                continue

            if now - pending[1] < debounce_s:
                continue

            body = turn_path.read_text(encoding="utf-8").strip()
            if not body:
                pending = None
                continue

            logger.info("Ejecutando meta-loop tras estabilizar archivo...")
            code = run_meta_loop(out, goal=goal, model=model, cursor_turn_file=cursor_turn_file)

            if code == 2:
                logger.warning("Sin contenido útil; no se actualiza mtime de referencia.")
                pending = None
                continue

            last_executed_mtime = turn_path.stat().st_mtime
            pending = None

            if exit_on_stop and _is_stop_instruction(out):
                logger.info("next_instruction.md indica STOP — salida por META_WATCH_EXIT_ON_STOP.")
                return

            if code == 1:
                logger.info("Meta-loop devolvió STOP/límite/error; el watcher sigue (nuevo edit re-dispara). Ctrl+C para salir.")

    except KeyboardInterrupt:
        logger.info("Watcher detenido por usuario.")


def main() -> None:
    import argparse

    from paper_pipeline.env import load_dotenv_if_available

    load_dotenv_if_available()

    parser = argparse.ArgumentParser(description="Vigila cursor_turn.md y ejecuta paper-meta-loop automáticamente.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--goal", type=str, default=_DEFAULT_GOAL)
    parser.add_argument("--model", type=str, default="best")
    args = parser.parse_args()
    watch_cursor_turn(args.output_dir, goal=args.goal, model=args.model)
    sys.exit(0)


if __name__ == "__main__":
    main()
