"""
ACREVIA - Risk Assessment Record Model.
Stores evaluated agrometeorological risk for a plot and crop season.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class RiskAssessmentRecord(Base, TimestampMixin):
    __tablename__ = "risk_assessment_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), nullable=True)
    
    evaluation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False
    )
    
    overall_risk_level: Mapped[str] = mapped_column(String(20), default="LOW", index=True, nullable=False)  # LOW, MODERATE, HIGH, INSUFFICIENT_DATA
    weather_data_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("weather_data.id", ondelete="SET NULL"), nullable=True)
    
    rules_triggered_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    advisory_en: Mapped[str] = mapped_column(Text, nullable=False)
    advisory_te: Mapped[str] = mapped_column(Text, nullable=False)
    advisory_hi: Mapped[str] = mapped_column(Text, nullable=False)
    
    limitations_notice: Mapped[str] = mapped_column(
        Text,
        default="High environmental risk denotes favorable climatic conditions for pathogen proliferation, NOT confirmed disease outbreak. Physical scouting required.",
        nullable=False
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")
    farm: Mapped["Farm"] = relationship("Farm")
    weather: Mapped[Optional["WeatherData"]] = relationship("WeatherData")

    __table_args__ = (
        Index("ix_risk_assessments_plot_time", "plot_id", "evaluation_timestamp"),
    )
