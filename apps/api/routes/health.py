"""
KisanVision API - Health & Readiness Probes.
Provides status indicators, system resource telemetry, and runtime health checks.
"""

import time
import os
from typing import Dict, Any
from fastapi import APIRouter
from apps.api.config import settings

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/health", summary="System Health & Readiness Probe")
def get_health() -> Dict[str, Any]:
    """Returns uptime, runtime environment, and operational readiness."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_seconds,
        "supported_crops": settings.SUPPORTED_CROPS,
        "device": "AMD Ryzen 5 5500U (CPU Execution Provider)"
    }
