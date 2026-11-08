"""
ACREVIA - System Status & Integration Health Endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.integrations.ml_client import ml_client
from backend.app.integrations.weather_client import weather_client
from backend.app.integrations.storage import get_storage_provider

router = APIRouter(prefix="/system", tags=["System & Integrations"])


@router.get("/info")
def get_system_info() -> Dict[str, Any]:
    """
    Returns platform identity, supported crops, geographic bounds, and service versions.
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "description": "ACREVIA Agricultural Intelligence Platform",
        "target_geography": "Telangana, India",
        "supported_crops": ["cotton", "rice", "chilli"],
        "supported_languages": ["te", "en", "hi"],
        "version": "1.0.0",
        "status": "OPERATIONAL"
    }


@router.get("/observability")
def get_system_observability() -> Dict[str, Any]:
    """
    Production observability endpoint providing pool statistics, telemetry, and service health.
    """
    from backend.app.database.session import engine

    pool_stats = {
        "pool_size": getattr(engine.pool, "size", lambda: 0)(),
        "checkedin": getattr(engine.pool, "checkedin", lambda: 0)(),
        "checkedout": getattr(engine.pool, "checkedout", lambda: 0)(),
        "overflow": getattr(engine.pool, "overflow", lambda: 0)(),
    }

    return {
        "service": "ACREVIA API Gateway",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database_pool": pool_stats,
        "supported_crops": settings.SUPPORTED_CROPS,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "storage_provider": settings.STORAGE_PROVIDER,
        "status": "HEALTHY"
    }



@router.get("/integrations")
async def get_integration_status() -> Dict[str, Any]:
    """
    Checks operational connectivity across internal and external integrated services.
    """
    ml_health = await ml_client.check_health()
    weather_sample = await weather_client.get_district_weather("warangal")

    storage = get_storage_provider()
    storage_status = "CONFIGURED" if storage else "UNAVAILABLE"

    return {
        "storage": {
            "provider": "LOCAL_SECURE",
            "status": storage_status
        },
        "ml_inference_microservice": {
            "status": ml_health.get("status", "UNAVAILABLE"),
            "endpoint": settings.ML_INFERENCE_URL,
            "details": ml_health
        },
        "weather_provider": {
            "provider": "Open-Meteo",
            "status": weather_sample.get("status", "CONFIGURED"),
            "district_tested": "warangal"
        }
    }
