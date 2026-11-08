"""
ACREVIA - AI Diagnosis & Expert Review Models.
Tracks the complete inference lifecycle, uncertainty metrics, and human agronomist validation.
"""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class DiagnosisRequest(Base, TimestampMixin):
    __tablename__ = "diagnosis_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    observation_id: Mapped[str] = mapped_column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), index=True, nullable=False)
    media_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("observation_media.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False)  # CREATED, IMAGE_VALIDATED, QUEUED, PROCESSING, COMPLETED, NEEDS_REVIEW, FAILED
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    observation: Mapped["Observation"] = relationship("Observation", back_populates="diagnoses")
    prediction: Mapped[Optional["Prediction"]] = relationship("Prediction", back_populates="diagnosis_request", uselist=False, cascade="all, delete-orphan")
    expert_review: Mapped[Optional["ExpertReview"]] = relationship("ExpertReview", back_populates="diagnosis_request", uselist=False, cascade="all, delete-orphan")


class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diagnosis_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("diagnosis_requests.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_state: Mapped[str] = mapped_column(String(50), nullable=False)  # One of the 8 agricultural decision states
    top_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    normalized_entropy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_margin: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cibrc_advisory: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Relationships
    diagnosis_request: Mapped["DiagnosisRequest"] = relationship("DiagnosisRequest", back_populates="prediction")
    candidates: Mapped[List["PredictionCandidate"]] = relationship("PredictionCandidate", back_populates="prediction", cascade="all, delete-orphan")


class PredictionCandidate(Base):
    __tablename__ = "prediction_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_id: Mapped[str] = mapped_column(String(36), ForeignKey("predictions.id", ondelete="CASCADE"), index=True, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    class_id: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name_te: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name_hi: Mapped[str] = mapped_column(String(100), nullable=False)
    pathogen_or_cause: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    calibrated_prob: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    prediction: Mapped["Prediction"] = relationship("Prediction", back_populates="candidates")


class ExpertReview(Base, TimestampMixin):
    __tablename__ = "expert_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diagnosis_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("diagnosis_requests.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    expert_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING, CONFIRMED, OVERRIDDEN
    verified_class_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expert_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    diagnosis_request: Mapped["DiagnosisRequest"] = relationship("DiagnosisRequest", back_populates="expert_review")
