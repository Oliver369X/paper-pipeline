"""CLI: `paper-racing-loop` — N rondas de Cursor CLI para construir el juego en outputs/code/X."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from paper_pipeline.constants import ExitCode
from paper_pipeline.cursor_cli_runner import run_cursor_cli
from paper_pipeline.env import load_dotenv_if_available
from paper_pipeline.mission import load_mission
from paper_pipeline.racing_prompts import GAME_REL, improvement_loop_prompt, round_prompts

logger = logging.getLogger(__name__)


def _ensure_methodology(out: Path, mission_dir: Path) -> None:
    spec = mission_dir / "game_spec.md"
    out.mkdir(parents=True, exist_ok=True)
    meth = out / "methodology.md"
    if meth.is_file() and meth.read_text(encoding="utf-8").strip():
        return
    if spec.is_file():
        body = (
            "# Metodología (generada desde game_spec.md)\n\n"
            + spec.read_text(encoding="utf-8")
        )
    else:
        body = f"# Metodología\n\nJuego 3D MVP bajo `{GAME_REL}/`.\n"
    meth.write_text(body, encoding="utf-8")


def _full_prompt(*, title: str, body: str, mission_topic: str) -> str:
    return (
        f"# {title}\n\n"
        f"Contexto de misión: {mission_topic}\n\n"
        f"{body}\n"
    )


def main() -> None:
    load_dotenv_if_available()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta varias rondas del agente Cursor (CLI) para generar el juego bajo outputs/code/X. "
            "Modelo recomendado: definí CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast en .env"
        ),
    )
    parser.add_argument(
        "mission",
        nargs="?",
        type=Path,
        default=Path("missions/racing_game_3d/mission.md"),
        help="Ruta a mission.md (default: missions/racing_game_3d/mission.md)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=6,
        help="Número de rondas (default: 6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No llama al agente; solo prepara methodology y lista rondas",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help=(
            "Tras las rondas iniciales, ejecuta un bucle de refinamiento continuo "
            "(calidad, buenas prácticas, robustez) hasta --loop-max iteraciones"
        ),
    )
    parser.add_argument(
        "--loop-max",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Máximo de iteraciones del bucle --loop (default: env RACING_LOOP_MAX o 12)"
        ),
    )
    args = parser.parse_args()

    loop_max = args.loop_max
    if loop_max is None:
        try:
            loop_max = int(os.environ.get("RACING_LOOP_MAX", "12"))
        except ValueError:
            loop_max = 12
    loop_max = max(1, loop_max)

    mission_path = args.mission.resolve()
    if not mission_path.is_file():
        logger.error("No existe la misión: %s", mission_path)
        sys.exit(ExitCode.MISSION_NOT_FOUND)

    mission = load_mission(mission_path)
    mission_dir = mission_path.parent
    out = (mission_dir / mission.output_dir).resolve()
    _ensure_methodology(out, mission_dir)

    rounds = round_prompts()[: max(1, args.rounds)]
    extra = os.environ.get("CURSOR_AGENT_EXTRA_ARGS", "").strip()
    if not args.dry_run and "composer" not in extra.lower() and "model" not in extra.lower():
        logger.warning(
            "CURSOR_AGENT_EXTRA_ARGS no parece fijar modelo; para Composer 2 Fast usá: "
            "CURSOR_AGENT_EXTRA_ARGS=--model composer-2-fast"
        )

    for i, (title, body) in enumerate(rounds, start=1):
        logger.info("=== %s ===", title)
        prompt = _full_prompt(title=title, body=body, mission_topic=mission.topic)
        if args.dry_run:
            logger.info("Dry-run: prompt length=%s chars", len(prompt))
            continue
        code = run_cursor_cli(
            cwd=mission_dir,
            output_dir=out,
            mission=mission,
            prompt=prompt,
            dry_run=False,
        )
        if code != 0:
            logger.error("Ronda %s falló con código %s", i, code)
            sys.exit(code)

    if args.loop:
        logger.info(
            "=== Bucle de mejora continua (--loop): %s iteraciones máx. ===",
            loop_max,
        )
        for j in range(1, loop_max + 1):
            title, body = improvement_loop_prompt(iteration=j, max_iter=loop_max)
            logger.info("=== %s ===", title)
            prompt = _full_prompt(title=title, body=body, mission_topic=mission.topic)
            if args.dry_run:
                logger.info("Dry-run [loop]: prompt length=%s chars", len(prompt))
                continue
            code = run_cursor_cli(
                cwd=mission_dir,
                output_dir=out,
                mission=mission,
                prompt=prompt,
                dry_run=False,
            )
            if code != 0:
                logger.error("Bucle mejora iteración %s falló con código %s", j, code)
                sys.exit(code)

    if args.dry_run:
        n_loop = loop_max if args.loop else 0
        logger.info(
            "Dry-run OK: %s rondas iniciales + %s iteraciones de mejora planificadas",
            len(rounds),
            n_loop,
        )
    else:
        logger.info("Listo. Juego en: %s", out / "code" / "X")

    sys.exit(0)


if __name__ == "__main__":
    main()
