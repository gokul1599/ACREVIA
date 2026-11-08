"""
ACREVIA - Models Package.
Exports all SQLAlchemy ORM entities for Alembic discovery and application use.
"""

from backend.app.database.base import Base, TimestampMixin
from backend.app.models.user import User, Role, UserRole, SessionToken
from backend.app.models.farm import Farm, FarmMembership, Plot, Plant
from backend.app.models.crop import Crop, CropVariety, CropSeason, CropStageEvent
from backend.app.models.observation import Observation, ObservationMedia, ImageQualityAssessment
from backend.app.models.diagnosis import DiagnosisRequest, Prediction, PredictionCandidate, ExpertReview
from backend.app.models.operation import FarmOperation, WeatherObservation, RiskAssessment
from backend.app.models.governance import ConsentRecord, AuditLog
from backend.app.models.knowledge_source import KnowledgeSource
from backend.app.models.knowledge_document import KnowledgeDocument, KnowledgeDocumentVersion
from backend.app.models.knowledge_chunk import KnowledgeChunk
from backend.app.models.knowledge_embedding import KnowledgeEmbedding
from backend.app.models.ingestion_job import IngestionJob
from backend.app.models.knowledge_feedback import KnowledgeFeedback

# Stage 7 Models
from backend.app.models.weather_data import WeatherData
from backend.app.models.risk_rule import RiskRule
from backend.app.models.risk_assessment import RiskAssessmentRecord
from backend.app.models.risk_alert import RiskAlert
from backend.app.models.expert_profile import ExpertProfile
from backend.app.models.expert_case import ExpertReviewCase
from backend.app.models.expert_assessment import ExpertAssessment, ExpertAssessmentRevision
from backend.app.models.intervention import InterventionRecord, OutcomeObservation

# Stage 9 Models (Phase II Precision Agriculture)
from backend.app.models.geo_spatial import PlotGeometry, LocationPermission
from backend.app.models.satellite import SatelliteSource, SatelliteAcquisition, SatelliteObservation, SATELLITE_EVIDENCE_DISCLAIMER
from backend.app.models.sensor import SensorDevice, SensorMeasurement, SensorCalibration
from backend.app.models.evidence_fusion import FusionExplanation
from backend.app.models.yield_research import HarvestMeasurement, YieldForecastRecord
from backend.app.models.knowledge_graph import KnowledgeEntity, KnowledgeRelationship

# Stage 10 Models (Intelligent Farm Digital Twin & Decision Intelligence)
from backend.app.models.digital_twin import FarmTwin, TwinSnapshot, TwinStateRecord, TwinSynchronizationEvent
from backend.app.models.simulation import SimulationScenario, SimulationResult
from backend.app.models.optimization import OptimizationProblem, OptimizationResult
from backend.app.models.crop_planning import CropCalendarDefinition, CropTask
from backend.app.models.decision_intelligence import DecisionRecord, DecisionFeedback

# Stage 11 Models (Agricultural Economics, Market Analytics & Produce Traceability)
from backend.app.models.financial_ledger import FarmExpense, FinancialCorrection, SaleTransaction
from backend.app.models.market_intelligence import MarketLocation, MarketCommodity, MarketPriceObservation
from backend.app.models.harvest_operations import HarvestPlan, HarvestSession
from backend.app.models.produce_traceability import ProduceLot, LotMovement
from backend.app.models.post_harvest import ProduceQualityProfile, QualityMeasurement, StorageLocation, StorageLot
from backend.app.models.crop_economics import CropSeasonEconomics
from backend.app.models.evidence_package import CropLossEvidencePackage

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Role",
    "UserRole",
    "SessionToken",
    "Farm",
    "FarmMembership",
    "Plot",
    "Plant",
    "Crop",
    "CropVariety",
    "CropSeason",
    "CropStageEvent",
    "Observation",
    "ObservationMedia",
    "ImageQualityAssessment",
    "DiagnosisRequest",
    "Prediction",
    "PredictionCandidate",
    "ExpertReview",
    "FarmOperation",
    "WeatherObservation",
    "RiskAssessment",
    "ConsentRecord",
    "AuditLog",
    "KnowledgeSource",
    "KnowledgeDocument",
    "KnowledgeDocumentVersion",
    "KnowledgeChunk",
    "KnowledgeEmbedding",
    "IngestionJob",
    "KnowledgeFeedback",
    # Stage 7 exports
    "WeatherData",
    "RiskRule",
    "RiskAssessmentRecord",
    "RiskAlert",
    "ExpertProfile",
    "ExpertReviewCase",
    "ExpertAssessment",
    "ExpertAssessmentRevision",
    "InterventionRecord",
    "OutcomeObservation",
    # Stage 9 exports
    "PlotGeometry",
    "LocationPermission",
    "SatelliteSource",
    "SatelliteAcquisition",
    "SatelliteObservation",
    "SATELLITE_EVIDENCE_DISCLAIMER",
    "SensorDevice",
    "SensorMeasurement",
    "SensorCalibration",
    "FusionExplanation",
    "HarvestMeasurement",
    "YieldForecastRecord",
    "KnowledgeEntity",
    "KnowledgeRelationship",
    # Stage 10 exports
    "FarmTwin",
    "TwinSnapshot",
    "TwinStateRecord",
    "TwinSynchronizationEvent",
    "SimulationScenario",
    "SimulationResult",
    "OptimizationProblem",
    "OptimizationResult",
    "CropCalendarDefinition",
    "CropTask",
    "DecisionRecord",
    "DecisionFeedback",
    # Stage 11 exports
    "FarmExpense",
    "FinancialCorrection",
    "SaleTransaction",
    "MarketLocation",
    "MarketCommodity",
    "MarketPriceObservation",
    "HarvestPlan",
    "HarvestSession",
    "ProduceLot",
    "LotMovement",
    "ProduceQualityProfile",
    "QualityMeasurement",
    "StorageLocation",
    "StorageLot",
    "CropSeasonEconomics",
    "CropLossEvidencePackage",
]
