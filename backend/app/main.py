"""
QueryNest FastAPI application entry point.

Registers all API routers and configures CORS.
Database schema changes are managed by Alembic migrations.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.query import router as query_router
from app.api.upload import router as upload_router
from app.api.conversations import router as conversations_router
from app.api.voice import router as voice_router
from app.api.knowledge_base import router as knowledge_base_router
# -------------------------------------------------------------
# Milestone 4 imports
# -------------------------------------------------------------
from app.analytics.router import router as analytics_router
from app.knowledge_gaps.router import router as knowledge_gaps_router
from app.admin.router import router as admin_router
from app.core.config import CORS_ALLOW_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.

    Database schema management is handled separately
    through Alembic migrations.
    """
    yield


# Create the FastAPI application.
app = FastAPI(
    title="QueryNest",
    lifespan=lifespan,
)


# Configure CORS for frontend access.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register all API routes.
app.include_router(
    health_router
)

app.include_router(
    auth_router
)

app.include_router(
    documents_router
)

app.include_router(
    upload_router
)

app.include_router(
    query_router
)

app.include_router(
    conversations_router
)

app.include_router(
    voice_router
)

app.include_router(
    knowledge_base_router
)

# -------------------------------------------------------------
# Milestone 4 API routes
# -------------------------------------------------------------
app.include_router(
    analytics_router
)

app.include_router(
    knowledge_gaps_router
)

app.include_router(
    admin_router
)