"""
ACREVIA - Soil Health Intelligence Models (Pillar A).
Captures soil profiles, sampling lifecycle, accredited laboratory results, and analytical provenance.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class SoilProfile(Base, TimestampMixin):
    """Long-term soil pedon and physical profile definition for a plot."""
    __tablename__ = "soil_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    soil_order: Mapped[str] = mapped_column(String(50), default="VERTISOL", nullable=False)  # VERTISOL, ALFISOL, INCEPTISOL, ENTISOL
    soil_series_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    drainage_class: Mapped[str] = mapped_column(String(50), default="MODERATELY_WELL_DRAINED", nullable=False)
    bulk_density_g_cm3: Mapped[Optional[float]] = mapped_column(Float, default=1.35, nullable=True)
    effective_soil_depth_cm: Mapped[Optional[float]] = mapped_column(Float, default=90.0, nullable=True)
    texture_class: Mapped[str] = mapped_column(String(50), default="CLAY_LOAM", nullable=False)

    # Relationship
    samples: Mapped[List["SoilSample"]] = relationship("SoilSample", back_populates="profile", cascade="all, delete-orphan")


class SoilSample(Base, TimestampMixin):
    """Field soil sampling event with geo-location, composite core count, and provenance."""
    __tablename__ = "soil_samples"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    profile_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("soil_profiles.id", ondelete="SET NULL"), nullable=True)
    sampled_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    sample_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    sampling_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sampling_depth_min_cm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sampling_depth_max_cm: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    gps_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    composite_cores_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    spatial_coverage_warning: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g. INSUFFICIENT_SPATIAL_COVERAGE
    status: Mapped[str] = mapped_column(String(30), default="COLLECTED", nullable=False)  # COLLECTED, DISPATCHED_TO_LAB, ANALYZED, DISPUTED

    # Relationships
    profile: Mapped[Optional["SoilProfile"]] = relationship("SoilProfile", back_populates="samples")
    test_results: Mapped[List["SoilTestResult"]] = relationship("SoilTestResult", back_populates="sample", cascade="all, delete-orphan")


class SoilTestResult(Base, TimestampMixin):
    """Accredited laboratory analytical test certificate with explicit method provenance."""
    __tablename__ = "soil_test_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    soil_sample_id: Mapped[str] = mapped_column(String(36), ForeignKey("soil_samples.id", ondelete="CASCADE"), index=True, nullable=False)
    laboratory_name: Mapped[str] = mapped_column(String(150), nullable=False)
    accreditation_number: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Soil Chemical Properties
    ph: Mapped[float] = mapped_column(Float, nullable=False)
    electrical_conductivity_ec: Mapped[float] = mapped_column(Float, nullable=False)  # dS/m
    organic_carbon_percent: Mapped[float] = mapped_column(Float, nullable=False)     # %
    
    # Primary Macronutrients (kg/ha)
    available_nitrogen_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)
    available_phosphorus_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)
    available_potassium_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Secondary and Micronutrients (ppm / mg/kg)
    available_sulphur_ppm: Mapped[Optional[float]] = mapped_column(Float, default=12.0, nullable=True)
    available_zinc_ppm: Mapped[Optional[float]] = mapped_column(Float, default=0.75, nullable=True)
    available_iron_ppm: Mapped[Optional[float]] = mapped_column(Float, default=5.50, nullable=True)
    available_boron_ppm: Mapped[Optional[float]] = mapped_column(Float, default=0.60, nullable=True)
    
    # Provenance metadata
    provenance_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    sample: Mapped["SoilSample"] = relationship("SoilSample", back_populates="test_results")
