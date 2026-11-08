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
    "AuditLog"
]
