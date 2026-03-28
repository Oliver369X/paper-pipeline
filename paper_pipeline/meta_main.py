"""CLI for meta_loop."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from paper_pipeline.env import load_dotenv_if_available
from paper_pipeline.meta_loop import run_meta_loop


def main() -> None:
    load_dotenv_if_available()
    parser = argparse.ArgumentParser(
        description=(
            "Meta-agente: lee outputs/cursor_turn.md, pregunta a Perplexity qué hacer a continuación, "
            "escribe outputs/next_instruction.md. Límite de rondas: META_MAX_ROUNDS."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directorio de salida (default: outputs)",
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="Completar el paper pipeline: código bajo outputs/code/ alineado con methodology y experiments.",
        help="Objetivo global para el revisor",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4.6-thinking",
        help="Modelo Perplexity (default: claude-sonnet-4.6-thinking)",
    )
    args = parser.parse_args()
    code = run_meta_loop(args.output_dir, goal=args.goal, model=args.model)
    sys.exit(code)


if __name__ == "__main__":
    main()
