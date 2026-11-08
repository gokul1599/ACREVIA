"""
ACREVIA - Nutrient Intelligence & Governance Models (Pillar D).
Captures soil-test-driven N-P-K & micronutrient prescriptions, split schedules, and agronomist escalations.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class NutrientAssessment(Base, TimestampMixin):
    """Institutional nutrient diagnosis and split application prescription."""
    __tablename__ = "nutrient_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    soil_test_result_id: Mapped[str] = mapped_column(String(36), ForeignKey("soil_test_results.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_id: Mapped[str] = mapped_column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Sufficiency status
    nitrogen_status: Mapped[str] = mapped_column(String(30), default="SUFFICIENT", nullable=False)  # DEFICIENT, SUFFICIENT, EXCESS
    phosphorus_status: Mapped[str] = mapped_column(String(30), default="SUFFICIENT", nullable=False)
    potassium_status: Mapped[str] = mapped_column(String(30), default="SUFFICIENT", nullable=False)
    zinc_status: Mapped[str] = mapped_column(String(30), default="SUFFICIENT", nullable=False)
    boron_status: Mapped[str] = mapped_column(String(30), default="SUFFICIENT", nullable=False)

    # Doses (kg/ha)
    recommended_n_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_p2o5_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_k2o_kg_ha: Mapped[float] = mapped_column(Float, nullable=False)

    # Schedules & Recommendations
    split_application_schedule_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    micronutrient_recommendations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    
    # Guardrails & Citations
    safeguard_checks_passed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    institutional_citation: Mapped[str] = mapped_column(String(200), default="PJTSAU Package of Practices", nullable=False)

    # Relationships
    reviews: Mapped[List["NutrientExpertReview"]] = relationship("NutrientExpertReview", back_populates="assessment", cascade="all, delete-orphan")


class NutrientExpertReview(Base, TimestampMixin):
    """Expert agronomist review, validation, or modification of nutrient prescription."""
    __tablename__ = "nutrient_expert_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nutrient_assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("nutrient_assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    expert_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    review_status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, APPROVED, MODIFIED, REJECTED
    agronomist_notes: Mapped[str] = mapped_column(Text, nullable=False)
    revised_prescription_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    assessment: Mapped["NutrientAssessment"] = relationship("NutrientAssessment", back_populates="reviews")
