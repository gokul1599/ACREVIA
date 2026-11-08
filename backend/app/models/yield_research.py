"""
ACREVIA - Predictive Agriculture & Yield Feasibility Models (Pillar E: Acrevia Predict).
Stores ground-truth harvest measurements and governed yield prediction feasibility records
with strict epistemic withholding safeguards.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class HarvestMeasurement(Base, TimestampMixin):
    __tablename__ = "harvest_measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    
    harvest_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    yield_quintals_per_acre: Mapped[float] = mapped_column(Float, nullable=False)
    total_harvest_kg: Mapped[float] = mapped_column(Float, nullable=False)
    
    provenance_tier: Mapped[str] = mapped_column(String(50), nullable=False)  # TIER_1_VERIFIED_WEIGHBRIDGE, TIER_2_CCE_CUT, TIER_3_FARMER_REPORT
    verification_document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    season: Mapped["CropSeason"] = relationship("CropSeason")

    __table_args__ = (
        Index("ix_harvest_plot_season", "plot_id", "season_id"),
    )


class YieldForecastRecord(Base, TimestampMixin):
    __tablename__ = "yield_forecast_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    
    model_version: Mapped[str] = mapped_column(String(50), default="acrevia-predict-v0.9.0", nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # WITHHELD_INSUFFICIENT_DATA, READY_FOR_PILOT, RESEARCH_ONLY
    
    predicted_yield_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_yield_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    withholding_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    features_snapshot_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    season: Mapped["CropSeason"] = relationship("CropSeason")
