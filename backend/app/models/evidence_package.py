"""
ACREVIA - Crop Loss Evidence Package Model.
Cryptographically verified evidence bundles for crop damage, disaster relief, and PMFBY claims.
"""

from datetime import date, datetime, timezone
import uuid
from typing import Optional
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.base import Base


class CropLossEvidencePackage(Base):
    __tablename__ = "crop_loss_evidence_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)

    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EXCESS_RAINFALL, CYCLONE_WIND, HAILSTORM, EXTREME_DROUGHT, PEST_OUTBREAK
    package_payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    package_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 integrity hash
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("ix_evidence_farm_season", "farm_id", "crop_season_id"),
    )
