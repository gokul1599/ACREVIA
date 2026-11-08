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

# Stage 10 Routers (Farm Digital Twin & Decision Intelligence)
from backend.app.api.v1.endpoints.twin import router as twin_router
from backend.app.api.v1.endpoints.simulations import router as simulations_router
from backend.app.api.v1.endpoints.optimization import router as optimization_router
from backend.app.api.v1.endpoints.planning import router as planning_router
from backend.app.api.v1.endpoints.decisions import router as decisions_router

# Stage 11 Routers (Agricultural Economics, Market Analytics, Harvest & Produce Traceability)
from backend.app.api.v1.endpoints.ledger import router as ledger_router
from backend.app.api.v1.endpoints.market import router as market_router
from backend.app.api.v1.endpoints.harvest import router as harvest_router
from backend.app.api.v1.endpoints.quality import router as quality_router
from backend.app.api.v1.endpoints.trace import router as trace_router
from backend.app.api.v1.endpoints.economics import router as economics_router

# Stage 12 Routers (Phase III Collaborative Intelligence, Collectives & Regional Pulse)
from backend.app.api.v1.endpoints.connect import router as connect_router
from backend.app.api.v1.endpoints.commons import router as commons_router
from backend.app.api.v1.endpoints.collectives import router as collectives_router
from backend.app.api.v1.endpoints.research import router as research_router
from backend.app.api.v1.endpoints.extension import router as extension_router
from backend.app.api.v1.endpoints.regional_pulse import router as regional_pulse_router

# Stage 13 Routers (Phase IV Climate-Resilient & Sustainable Agriculture)
from backend.app.api.v1.endpoints.soil import router as soil_router
from backend.app.api.v1.endpoints.water import router as water_router
from backend.app.api.v1.endpoints.climate import router as climate_router
from backend.app.api.v1.endpoints.nutrient import router as nutrient_router
from backend.app.api.v1.endpoints.sustain import router as sustain_router
from backend.app.api.v1.endpoints.resilience import router as resilience_router

# Stage 14 Routers (Interoperability, Open API, Partner Integrations & Data Exchange)
from backend.app.api.v1.endpoints.exchange import router as exchange_router
from backend.app.api.v1.endpoints.partners import router as partners_router
from backend.app.api.v1.endpoints.developer import router as developer_router
from backend.app.api.v1.endpoints.consent_grants import router as consent_grants_router
from backend.app.api.v1.endpoints.webhooks import router as webhooks_router
from backend.app.api.v1.endpoints.standards import router as standards_router

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

# Stage 10 Routes
api_v1_router.include_router(twin_router)
api_v1_router.include_router(simulations_router)
api_v1_router.include_router(optimization_router)
api_v1_router.include_router(planning_router)
api_v1_router.include_router(decisions_router)

# Stage 11 Routes
api_v1_router.include_router(ledger_router)
api_v1_router.include_router(market_router)
api_v1_router.include_router(harvest_router)
api_v1_router.include_router(quality_router)
api_v1_router.include_router(trace_router)
api_v1_router.include_router(economics_router)

# Stage 12 Routes (Collaborative Intelligence, Collectives, Research & Regional Pulse)
api_v1_router.include_router(connect_router)
api_v1_router.include_router(commons_router)
api_v1_router.include_router(collectives_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(extension_router)
api_v1_router.include_router(regional_pulse_router)

# Stage 13 Routes (Soil Health, Water Intelligence, Climate Resilience, Nutrient Governance & Sustainability)
api_v1_router.include_router(soil_router)
api_v1_router.include_router(water_router)
api_v1_router.include_router(climate_router)
api_v1_router.include_router(nutrient_router)
api_v1_router.include_router(sustain_router)
api_v1_router.include_router(resilience_router)

# Stage 14 Routes (Agricultural Interoperability, Open API & Partner Integrations)
api_v1_router.include_router(exchange_router)
api_v1_router.include_router(partners_router)
api_v1_router.include_router(developer_router)
api_v1_router.include_router(consent_grants_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(standards_router)
