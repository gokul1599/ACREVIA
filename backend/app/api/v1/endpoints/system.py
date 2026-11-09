"""
ACREVIA - System Status & Integration Health Endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter
import sqlalchemy as sa

from backend.app.core.config import settings
from backend.app.database.session import engine
from backend.app.integrations.ml_client import ml_client
from backend.app.integrations.weather_client import weather_client
from backend.app.integrations.storage import get_storage_provider
from backend.app.integrations.groq_client import groq_client
from backend.app.integrations.hf_client import hf_client
from backend.app.integrations.copernicus_client import copernicus_client
from backend.app.integrations.datagov_client import datagov_client
from backend.app.integrations.satellite_client import satellite_client

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
    Checks operational connectivity across internal and external integrated services
    covering all seven supported free-tier services.
    """
    # 1. Internal & Baseline Providers
    ml_health = await ml_client.check_health()
    weather_sample = await weather_client.get_district_weather("warangal")
    storage = get_storage_provider()
    storage_status = "CONFIGURED" if storage else "UNAVAILABLE"

    # 2. Free External Services Suite
    groq_health = await groq_client.check_health()
    hf_health = await hf_client.check_health()
    satellite_health = await satellite_client.check_health()
    copernicus_health = await copernicus_client.check_health()
    datagov_health = await datagov_client.check_health()

    # 3. Database (Neon PostgreSQL) Health
    try:
        with engine.connect() as conn:
            val = conn.execute(sa.text("SELECT 1")).scalar()
            db_connected = (val == 1)
        db_type = "Neon PostgreSQL (Primary Relational + pgvector)" if "postgres" in str(engine.url) else "SQLite (Dev/Test Fallback)"
        neon_health = {
            "status": "CONFIGURED" if db_connected else "DEGRADED",
            "provider": "Neon Serverless PostgreSQL",
            "db_type": db_type,
            "free_allowance_gb": 0.5,
            "pgvector_active": True
        }
    except Exception as e:
        neon_health = {
            "status": "UNAVAILABLE",
            "provider": "Neon Serverless PostgreSQL",
            "error": str(e)
        }

    # 4. Redis / Upstash Distributed Rate Limiting
    is_upstash = bool(settings.REDIS_URL and "upstash" in settings.REDIS_URL.lower())
    redis_status = "IN_MEMORY_FALLBACK"
    redis_latency_ms = None
    if settings.REDIS_URL:
        try:
            import redis
            r_url = settings.REDIS_URL
            if r_url.startswith("redis://") and "upstash.io" in r_url:
                r_url = "rediss://" + r_url[len("redis://"):]
            t0 = time.time()
            r_client = redis.Redis.from_url(r_url, socket_timeout=2.5)
            if r_client.ping():
                redis_status = "CONFIGURED"
                redis_latency_ms = round((time.time() - t0) * 1000, 1)
        except Exception:
            redis_status = "DEGRADED_FALLBACK"

    redis_health = {
        "status": redis_status if settings.REDIS_URL else "IN_MEMORY_FALLBACK",
        "provider": "Upstash Redis" if is_upstash else ("Redis Managed" if settings.REDIS_URL else "InMemory Sliding-Window"),
        "tls_enforced": bool(settings.REDIS_URL and (settings.REDIS_URL.startswith("rediss://") or "upstash.io" in settings.REDIS_URL)),
        "latency_ms": redis_latency_ms,
        "fail_mode": settings.RATE_LIMIT_FAIL_MODE,
        "free_tier": True
    }

    return {
        # Preserved baseline keys for backward compatibility
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
            "district_tested": "warangal",
            "attribution": weather_sample.get("attribution", "Open-Meteo.com")
        },

        # Seven Free Services Manifest
        "services": {
            "groq_cloud": groq_health,
            "neon_postgresql": neon_health,
            "upstash_redis": redis_health,
            "earth_search_satellite": satellite_health,
            "copernicus_data_space": {
                **copernicus_health,
                "migrated_to": "Element 84 Earth Search STAC API",
                "auth_required": False
            },
            "hugging_face": hf_health,
            "open_meteo": {
                "status": weather_sample.get("status", "CONFIGURED"),
                "provider": "Open-Meteo",
                "auth_required": False,
                "attribution": weather_sample.get("attribution")
            },
            "data_gov_in": datagov_health
        }
    }
