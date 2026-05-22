from fastapi import APIRouter

from app.api.v1.endpoints import cjm, health, projects
from app.core.config import settings


api_router = APIRouter(prefix=settings.API_V1_PREFIX)
api_router.include_router(health.router)
api_router.include_router(projects.router)
api_router.include_router(cjm.router)
