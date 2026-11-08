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
        "version": "1.0.0-stage4",
        "status": "OPERATIONAL"
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
