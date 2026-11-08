"""
ACREVIA - Multi-Source Evidence Fusion Models (Pillar D: Acrevia Fusion).
Stores cross-stream synthesized assessments, detected contradictions,
and multilingual farmer explanations.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class FusionExplanation(Base, TimestampMixin):
    __tablename__ = "fusion_explanations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    
    evaluation_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    overall_vigor_status: Mapped[str] = mapped_column(String(50), nullable=False)  # OPTIMAL, MODERATE_STRESS, SEVERE_STRESS, VEGETATIVE_CLEARING
    primary_stress_driver: Mapped[str] = mapped_column(String(50), default="NONE", nullable=False)  # NONE, MOISTURE_DEFICIT, WATERLOGGING, HEAT_STRESS, PEST_DISEASE_SUSPECT, OPERATIONAL_CLEARING
    
    evidence_sources_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    contradictions_detected_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    farmer_explanation_en: Mapped[str] = mapped_column(Text, nullable=False)
    farmer_explanation_te: Mapped[str] = mapped_column(Text, nullable=False)
    farmer_explanation_hi: Mapped[str] = mapped_column(Text, nullable=False)
    
    epistemic_qualifications_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot")

    __table_args__ = (
        Index("ix_fusion_plot_eval_time", "plot_id", "evaluation_timestamp"),
    )
