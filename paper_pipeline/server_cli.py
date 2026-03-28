"""CLI: `paper-web` — arranca uvicorn para la API local."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    p = argparse.ArgumentParser(description="Servidor web paper-pipeline (FastAPI).")
    p.add_argument("--host", default="127.0.0.1", help="Host de escucha (default 127.0.0.1).")
    p.add_argument("--port", type=int, default=8000, help="Puerto (default 8000).")
    p.add_argument("--reload", action="store_true", help="Recarga al cambiar código.")
    args = p.parse_args()
    uvicorn.run(
        "paper_pipeline.server.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
