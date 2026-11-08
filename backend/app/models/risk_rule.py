"""
ACREVIA - Agronomic Risk Rule Model.
Defines versioned, evidence-backed environmental rules for target Telangana crops.
"""

import uuid
from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base, TimestampMixin


class RiskRule(Base, TimestampMixin):
    __tablename__ = "risk_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    crop: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # COTTON, RICE, CHILLI
    target_threat: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    applicable_growth_stages: Mapped[str] = mapped_column(String(255), nullable=False)  # comma-separated
    
    # Environmental Thresholds
    min_temp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_temp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_leaf_wetness_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_consecutive_wet_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    severity_level: Mapped[str] = mapped_column(String(20), default="MODERATE", nullable=False)  # LOW, MODERATE, HIGH
    
    # Multilingual Advisories
    advisory_en: Mapped[str] = mapped_column(Text, nullable=False)
    advisory_te: Mapped[str] = mapped_column(Text, nullable=False)
    advisory_hi: Mapped[str] = mapped_column(Text, nullable=False)
    
    evidence_citations_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    __table_args__ = (
        Index("ix_risk_rules_crop_active", "crop", "is_active"),
    )
