"""
ACREVIA - Agricultural Data Exchange & Portability Models.
Stage 14: Export/Import Jobs, Serialization Formats, Cryptographic Manifests, and Mapping Profiles.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class DataExchangeJob(Base, TimestampMixin):
    """
    Asynchronous or synchronous agricultural data export/import job with cryptographic manifest.
    """
    __tablename__ = "data_exchange_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    farm_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="SET NULL"), index=True, nullable=True
    )
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)  # EXPORT, IMPORT
    format: Mapped[str] = mapped_column(String(20), default="JSON", nullable=False)  # JSON, CSV, GEOJSON, ARCHIVE
    categories_json: Mapped[str] = mapped_column(Text, default='["ALL"]', nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), default="REQUESTED", index=True, nullable=False
    )  # REQUESTED, PROCESSING, COMPLETED, PARTIALLY_COMPLETED, FAILED, CANCELLED
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conflicts_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    manifest_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    redact_pii: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preserve_conflicts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class DataMappingProfile(Base):
    """
    Saved custom mapping profile for importing non-standard agricultural spreadsheets/APIs into ACREVIA standards.
    """
    __tablename__ = "data_mapping_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_format: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # CUSTOM_CSV, AGMIST_EXPORT, SOIL_HEALTH_CARD_CSV, IOT_JSON
    target_entity: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # SOIL_SAMPLE, PLOT_OBSERVATION, HARVEST_RECORD, MARKET_PRICE
    mapping_rules_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
