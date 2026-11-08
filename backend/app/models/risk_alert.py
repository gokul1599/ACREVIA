"""
ACREVIA - Risk Alert Model.
Manages idempotent alerting, notification states, and farmer acknowledgments.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    risk_assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("risk_assessment_records.id", ondelete="CASCADE"), index=True, nullable=False)
    
    alert_level: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # LOW, MODERATE, HIGH
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    
    message_en: Mapped[str] = mapped_column(Text, nullable=False)
    message_te: Mapped[str] = mapped_column(Text, nullable=False)
    message_hi: Mapped[str] = mapped_column(Text, nullable=False)
    
    recommended_actions_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    deduplication_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    plot: Mapped["Plot"] = relationship("Plot")
    assessment: Mapped["RiskAssessmentRecord"] = relationship("RiskAssessmentRecord")

    __table_args__ = (
        Index("ix_risk_alerts_farm_active", "farm_id", "is_acknowledged", "is_dismissed"),
    )
