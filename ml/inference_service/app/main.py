"""
KisanVision - Standalone Dedicated ML Inference Service.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from ml.inference_service.app.core.config import config
from ml.inference_service.app.api.routes import router

app = FastAPI(
    title=config.SERVICE_NAME,
    version=config.SERVICE_VERSION,
    description="Dedicated high-throughput CPU inference microservice for KisanVision edge computer vision models.",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_type": "InferenceServiceInternalError",
            "message": "Internal error during inference processing.",
            "detail": str(exc)
        }
    )

app.include_router(router)
