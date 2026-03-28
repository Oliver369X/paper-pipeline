"""Mission API: CRUD, runs/SSE, draft y loop (sub-routers)."""

from __future__ import annotations

from fastapi import APIRouter

from .missions_brain import router as brain_router
from .missions_cockpit import router as cockpit_router
from .missions_content import router as content_router
from .missions_crud import router as crud_router
from .missions_runs import router as runs_router

router = APIRouter(prefix="/api/missions", tags=["missions"])
router.include_router(crud_router)
router.include_router(runs_router)
router.include_router(content_router)
router.include_router(cockpit_router)
router.include_router(brain_router)
