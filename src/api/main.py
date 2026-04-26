"""
Application factory for AI WellnessVision FastAPI server.

Usage::

    # Development
    uvicorn src.api.main:app --reload --port 8000

    # Programmatic
    from src.api.main import create_app
    app = create_app()
"""

import logging
import os
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.database.postgres_auth import postgres_db

load_dotenv()

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Lifespan handler (startup / shutdown)
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Initialise shared resources on startup and clean up on shutdown."""
    # ── Startup ──
    Path("uploads").mkdir(exist_ok=True)
    try:
        await postgres_db.initialize()
        logger.info("✅ Database pool initialised")
    except Exception as exc:
        logger.warning("⚠️  Database init failed (running without DB): %s", exc)

    yield

    # ── Shutdown ──
    try:
        await postgres_db.close()
        logger.info("Database pool closed")
    except Exception:
        pass


# ──────────────────────────────────────────────
# App factory
# ──────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    - Registers all routers
    - Adds CORS from ``ALLOWED_ORIGINS`` env var
    - Installs global exception handlers (404, 422, 500)
    """
    application = FastAPI(
        title="AI Wellness Vision API",
        description="Backend API for AI-powered health and wellness analysis",
        version="2.0.0",
        lifespan=lifespan,
    )

    # ── CORS ──
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000"
    ).split(",")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ──
    _register_routers(application)

    # ── Exception handlers ──
    _register_exception_handlers(application)

    # ── Root / health endpoints ──
    _register_health_endpoints(application)

    return application


# ──────────────────────────────────────────────
# Router registration
# ──────────────────────────────────────────────

def _register_routers(app: FastAPI) -> None:
    from src.api.routers import auth, analysis, chat, voice, visual_qa

    app.include_router(auth.router)
    app.include_router(analysis.router)
    app.include_router(chat.router)
    app.include_router(voice.router)
    app.include_router(visual_qa.router)


# ──────────────────────────────────────────────
# Health / root
# ──────────────────────────────────────────────

def _register_health_endpoints(app: FastAPI) -> None:
    @app.get("/", tags=["health"])
    async def root():
        """Root endpoint."""
        return {
            "message": "AI Wellness Vision API is running!",
            "version": "2.0.0",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/health", tags=["health"])
    @app.get("/api/v1/health", tags=["health"])
    async def health_check():
        """Quick health check returning service statuses."""
        return {
            "status": "healthy",
            "services": {
                "api": "running",
                "database": "connected" if postgres_db.pool else "disconnected",
            },
            "timestamp": datetime.now().isoformat(),
        }


# ──────────────────────────────────────────────
# Exception handlers
# ──────────────────────────────────────────────

def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=404,
            content={
                "detail": exc.detail if hasattr(exc, "detail") else "Resource not found",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request body validation failed",
                "errors": exc.errors(),
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        logger.error("Internal error on %s: %s\n%s", request.url.path, exc, traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected internal error occurred",
                "path": str(request.url.path),
            },
        )


# ──────────────────────────────────────────────
# Module-level app instance (for uvicorn CLI)
# ──────────────────────────────────────────────

app = create_app()


# ──────────────────────────────────────────────
# Direct execution
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("Starting AI Wellness Vision API Server …")
    print("  Flutter connects to: http://localhost:8000")
    print("  API docs:            http://localhost:8000/docs")
    print("  Health check:        http://localhost:8000/api/v1/health")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
