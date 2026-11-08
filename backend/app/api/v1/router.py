"""
ACREVIA - API v1 Master Router Assembly.
Integrates enterprise domains: Auth, Farms, Diagnoses, KrishiBrain RAG, RiskCast, ExpertConnect, and Interventions.
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
from backend.app.api.v1.endpoints.knowledge import router as knowledge_router
from backend.app.api.v1.endpoints.riskcast import router as riskcast_router
from backend.app.api.v1.endpoints.expertconnect import router as expertconnect_router
from backend.app.api.v1.endpoints.interventions import router as interventions_router

# Stage 9 Routers (Phase II Precision Agriculture)
from backend.app.api.v1.endpoints.geospatial import router as geospatial_router
from backend.app.api.v1.endpoints.satellite import router as satellite_router
from backend.app.api.v1.endpoints.sense import router as sense_router
from backend.app.api.v1.endpoints.fusion import router as fusion_router
from backend.app.api.v1.endpoints.predict import router as predict_router
from backend.app.api.v1.endpoints.knowledge_graph import router as knowledge_graph_router

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
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(riskcast_router)
api_v1_router.include_router(expertconnect_router)
api_v1_router.include_router(interventions_router)

# Stage 9 Routes
api_v1_router.include_router(geospatial_router)
api_v1_router.include_router(satellite_router)
api_v1_router.include_router(sense_router)
api_v1_router.include_router(fusion_router)
api_v1_router.include_router(predict_router)
api_v1_router.include_router(knowledge_graph_router)
