"""
ACREVIA - Sustainable Agriculture Models (Pillar E).
Captures sustainable practice taxonomies, farm practice records, empirical SOC tracking, and research GHG accounting.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin

SUSTAINABILITY_RESEARCH_DISCLAIMER = (
    "ACREVIA greenhouse gas estimations are research-grade indicative metrics based on "
    "IPCC Tier 1/2 factors. They do not constitute certified carbon credits or tradable offsets."
)


class AgriculturalPracticeDefinition(Base, TimestampMixin):
    """Canonical registry of evidence-backed sustainable farming practices."""
    __tablename__ = "agricultural_practice_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # SOIL_COVER, RESIDUE_MGMT, CROP_DIVERSITY, IPM, SOIL_WATER, ORGANIC_INPUT
    title_en: Mapped[str] = mapped_column(String(150), nullable=False)
    title_te: Mapped[str] = mapped_column(String(150), nullable=False)
    title_hi: Mapped[str] = mapped_column(String(150), nullable=False)
    description_en: Mapped[str] = mapped_column(Text, nullable=False)
    specification_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)


class FarmPracticeRecord(Base, TimestampMixin):
    """Verified logging of sustainable agricultural practice on a specific plot."""
    __tablename__ = "farm_practice_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    practice_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    implementation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    area_covered_acres: Mapped[float] = mapped_column(Float, nullable=False)
    verification_method: Mapped[str] = mapped_column(String(50), default="FARMER_LOG", nullable=False)  # FARMER_LOG, EXPERT_VERIFIED, GEO_TAGGED_IMAGE
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)  # ACTIVE, COMPLETED, DISCONTINUED


class SoilCarbonMeasurement(Base, TimestampMixin):
    """Empirical laboratory-verified soil organic carbon (SOC) time series."""
    __tablename__ = "soil_carbon_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    sample_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    depth_cm: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    soc_percent: Mapped[float] = mapped_column(Float, nullable=False)
    bulk_density: Mapped[Optional[float]] = mapped_column(Float, default=1.35, nullable=True)
    method: Mapped[str] = mapped_column(String(50), default="WALKLEY_BLACK", nullable=False)  # WALKLEY_BLACK, DRY_COMBUSTION
    lab_accreditation: Mapped[str] = mapped_column(String(100), default="NABL", nullable=False)


class EnvironmentalAccountingEstimate(Base, TimestampMixin):
    """Indicative research-grade greenhouse gas balance for seasonal operations."""
    __tablename__ = "environmental_accounting_estimates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    season: Mapped[str] = mapped_column(String(30), nullable=False)  # Kharif, Rabi, Summer
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    fertilizer_n2o_kg_co2e: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    paddy_ch4_kg_co2e: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fuel_combustion_kg_co2e: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_emissions_kg_co2e: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    emission_intensity_kg_co2e_per_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Always False (Non-certified research estimate)
    scientific_disclaimer: Mapped[str] = mapped_column(Text, default=SUSTAINABILITY_RESEARCH_DISCLAIMER, nullable=False)
