from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db

# Initialize Database Schema before app starts
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Quantum Signature Security & Threat Intelligence Engine API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Development fallback
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from app.api.v1.endpoints import health
app.include_router(health.router, prefix="/health", tags=["health"])

# Include routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

