from fastapi import APIRouter
from app.api.v1.endpoints import sessions, experiments, artifacts

api_router = APIRouter()
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(artifacts.router, prefix="/artifacts", tags=["artifacts"])
