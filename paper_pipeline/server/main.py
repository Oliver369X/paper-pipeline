"""FastAPI app: REST + SSE para la interfaz web local."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from paper_pipeline.brain.gemini_client import brain_sdk_available
from paper_pipeline.env import load_dotenv_if_available
from paper_pipeline.pipeline.common import _available_model_ids
from paper_pipeline.version import get_package_version

from .routers import missions
from .section_keys import OUTPUTS_HELP_ES, allowed_section_keys, section_meta_for_api

load_dotenv_if_available()


def _cors_allow_origins() -> list[str]:
    """Orígenes permitidos para el SPA (dev Vite + opcional lista en ``PAPER_PIPELINE_CORS_ORIGINS``)."""

    base = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]
    extra = os.environ.get("PAPER_PIPELINE_CORS_ORIGINS", "").strip()
    if not extra:
        return base
    merged = list(base)
    for part in extra.split(","):
        o = part.strip()
        if o and o not in merged:
            merged.append(o)
    return merged


app = FastAPI(title="paper-pipeline web")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(missions.router)


@app.get("/api/health")
def health() -> dict[str, object]:
    """Liveness + configuración mínima (sin llamadas lentas a APIs externas)."""

    p_token = os.environ.get("PERPLEXITY_SESSION_TOKEN", "").strip()
    n_token = os.environ.get("NOTION_TOKEN", "").strip()
    g_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if not g_key:
        brain_state = "missing"
    elif not brain_sdk_available():
        brain_state = "missing_sdk"
    else:
        brain_state = "configured"
    return {
        "status": "ok",
        "version": get_package_version(),
        "perplexity_session": "missing" if not p_token else "configured",
        "notion": "not_configured" if not n_token else "configured",
        "brain_gemini": brain_state,
    }


@app.get("/api/models")
def models() -> dict[str, list[str]]:
    return {"models": _available_model_ids()}


@app.get("/api/section-keys")
def section_keys() -> dict[str, object]:
    """Claves válidas, textos en español por sección y ayuda sobre dónde se escribe cada salida."""
    return {
        "keys": allowed_section_keys(),
        "meta": section_meta_for_api(),
        "outputs_help": OUTPUTS_HELP_ES,
    }


_static = Path(__file__).resolve().parents[2] / "web" / "dist"


def _safe_file_under_web_dist(rel: str) -> Path | None:
    """Resolve a path under ``web/dist`` without escaping the directory."""
    if not rel or rel.startswith(("/", "\\")) or ".." in Path(rel).parts:
        return None
    base = _static.resolve()
    try:
        p = (base / rel).resolve()
        p.relative_to(base)
    except (OSError, ValueError):
        return None
    return p


if _static.is_dir():
    _assets = _static / "assets"
    if _assets.is_dir():
        app.mount("/assets", StaticFiles(directory=_assets), name="spa_assets")

    @app.get("/")
    def spa_index() -> FileResponse:
        return FileResponse(_static / "index.html")

    @app.get("/{full_path:path}")
    def spa_or_static(full_path: str) -> FileResponse:
        # Rutas /api/* las cubren los routers y endpoints anteriores; esto es fallback SPA.
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        candidate = _safe_file_under_web_dist(full_path)
        if candidate is not None and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_static / "index.html")
