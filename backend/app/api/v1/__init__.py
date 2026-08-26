from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.admin.admin_controller import router as admin_router
from app.api.v1.articles.articles_controller import router as articles_router
from app.api.v1.categories.categories_controller import router as categories_router
from app.api.v1.sources.sources_controller import router as sources_router
from app.api.v1.timeline.timeline_controller import router as timeline_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(articles_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(timeline_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(admin_router)
