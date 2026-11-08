"""
ACREVIA - API v1 Master Router Assembly.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.farms import router as farms_router
from backend.app.api.v1.endpoints.plots import router as plots_router
from backend.app.api.v1.endpoints.seasons import router as seasons_router
from backend.app.api.v1.endpoints.observations import router as observations_router
from backend.app.api.v1.endpoints.diagnoses import router as diagnoses_router
from backend.app.api.v1.endpoints.expert_reviews import router as expert_reviews_router
from backend.app.api.v1.endpoints.weather import router as weather_router
from backend.app.api.v1.endpoints.consent import router as consent_router
from backend.app.api.v1.endpoints.system import router as system_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(farms_router)
api_v1_router.include_router(plots_router)
api_v1_router.include_router(seasons_router)
api_v1_router.include_router(observations_router)
api_v1_router.include_router(diagnoses_router)
api_v1_router.include_router(expert_reviews_router)
api_v1_router.include_router(weather_router)
api_v1_router.include_router(consent_router)
api_v1_router.include_router(system_router)
