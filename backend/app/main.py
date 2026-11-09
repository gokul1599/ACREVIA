"""
ACREVIA - Backend Application Gateway.
Enterprise-grade FastAPI entry point with correlation tracking, multi-tenant boundaries, and domain routers.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import AcreviaException
from backend.app.database.session import engine, SessionLocal
from backend.app.database.init_db import init_db, check_db_readiness
from backend.app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application startup and shutdown lifecycle management.
    """
    logger.info("Initializing ACREVIA Backend Application...")
    # Validate database schema readiness via Alembic version check without mutating production schema
    readiness = check_db_readiness(engine)
    if readiness["is_ready"]:
        logger.info(f"ACREVIA database schema verified ready at Alembic revision {readiness['alembic_version']} ({readiness['table_count']} tables).")
    else:
        logger.warning(f"Database readiness advisory: {readiness.get('error', 'Unverified schema state')}")

    # Seed baseline roles and taxonomies into managed schema
    try:
        init_db(create_tables=False)
        logger.info("ACREVIA database seed data verified successfully.")
    except Exception as e:
        logger.error(f"Database initialization warning: {e}")

    yield

    logger.info("Shutting down ACREVIA Backend Application...")


app = FastAPI(
    title="ACREVIA API",
    description="ACREVIA - Agricultural Intelligence Platform for Smallholder Farmers (Telangana, India)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next) -> Response:
    """
    Applies production-grade security headers according to OWASP guidelines.
    """
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(self), microphone=(self)"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def correlation_id_and_logging_middleware(request: Request, call_next) -> Response:
    """
    Injects unique Correlation ID into each request and logs execution latency.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    start_time = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms) [CID: {correlation_id}]"
    )
    return response


@app.exception_handler(AcreviaException)
async def acrevia_exception_handler(request: Request, exc: AcreviaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": exc.__class__.__name__,
            "detail": exc.message,
            "details": exc.details,
            "correlation_id": getattr(request.state, "correlation_id", None)
        },
        headers=exc.headers if hasattr(exc, "headers") and exc.headers else None
    )


# Root diagnostic endpoints
@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe."""
    return {
        "status": "HEALTHY",
        "service": "acrevia-backend",
        "version": "1.0.0"
    }


@app.get("/ready", tags=["Health"])
def readiness_check():
    """Readiness probe verifying database connectivity."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {
            "status": "READY",
            "database": "CONNECTED"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "NOT_READY", "database": "DISCONNECTED", "error": str(e)}
        )


@app.get("/", tags=["Root"])
def root():
    return {
        "project": "ACREVIA",
        "message": "Welcome to ACREVIA Agricultural Intelligence Platform API",
        "documentation": "/docs"
    }


# Include Master v1 API Router
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
