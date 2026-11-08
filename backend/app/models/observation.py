"""
ACREVIA - Observation & Foliar Media Models.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class Observation(Base, TimestampMixin):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), nullable=True)
    observer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    symptom_tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Comma-separated or JSON list of farmer-observed symptoms

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="observations")
    season: Mapped[Optional["CropSeason"]] = relationship("CropSeason", back_populates="observations")
    media: Mapped[List["ObservationMedia"]] = relationship("ObservationMedia", back_populates="observation", cascade="all, delete-orphan")
    diagnoses: Mapped[List["DiagnosisRequest"]] = relationship("DiagnosisRequest", back_populates="observation", cascade="all, delete-orphan")


class ObservationMedia(Base, TimestampMixin):
    __tablename__ = "observation_media"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    observation_id: Mapped[str] = mapped_column(String(36), ForeignKey("observations.id", ondelete="CASCADE"), index=True, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)  # image/jpeg, image/png
    sha256_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    observation: Mapped["Observation"] = relationship("Observation", back_populates="media")
    quality_assessment: Mapped[Optional["ImageQualityAssessment"]] = relationship("ImageQualityAssessment", back_populates="media", uselist=False, cascade="all, delete-orphan")


class ImageQualityAssessment(Base, TimestampMixin):
    __tablename__ = "image_quality_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id: Mapped[str] = mapped_column(String(36), ForeignKey("observation_media.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # ACCEPTED, RETAKE_OR_REVIEW, QUARANTINED
    sharpness_score: Mapped[float] = mapped_column(Float, nullable=False)
    exposure_status: Mapped[str] = mapped_column(String(50), nullable=False)
    reasons_json: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    media: Mapped["ObservationMedia"] = relationship("ObservationMedia", back_populates="quality_assessment")
