"""
KisanVision - FastAPI Application Gateway.
Agricultural Intelligence Platform API serving Telangana smallholder farmers,
extension workers, and agricultural research institutions.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from apps.api.config import settings
from apps.api.routes import health, vision

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Research-grade agricultural intelligence API for crop disease diagnosis, "
        "evidence-backed agronomic guidance, and CIBRC chemical safety compliance."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production via environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for uniform RFC 7807 error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": str(request.url)
        }
    )

# Include API v1 Routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(vision.router, prefix="/api/v1")


@app.get("/", summary="Root Index")
def root_index():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OPERATIONAL",
        "documentation": "/docs",
        "health_probe": "/api/v1/health",
        "vision_models": "/api/v1/vision/models"
    }
