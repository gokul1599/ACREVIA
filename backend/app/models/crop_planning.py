"""
ACREVIA - Crop Planning & Operations Models (Pillar D: ACREVIA Plan).
Stores PJTSAU crop calendar definitions, operations schedules, and dynamic weather conflict tracking.
"""

import uuid
from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Date, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class CropCalendarDefinition(Base, TimestampMixin):
    __tablename__ = "crop_calendar_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # COTTON, RICE, CHILLI
    variety_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    agro_climatic_zone: Mapped[str] = mapped_column(String(100), nullable=False)  # TELANGANA_NORTH_EASTERN, TELANGANA_SOUTHERN, TELANGANA_CENTRAL
    growth_stage: Mapped[str] = mapped_column(String(100), nullable=False)
    typical_duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_tasks_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_citation: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)

    tasks: Mapped[List["CropTask"]] = relationship("CropTask", back_populates="calendar_def")


class CropTask(Base, TimestampMixin):
    __tablename__ = "crop_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    calendar_def_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_calendar_definitions.id", ondelete="SET NULL"), nullable=True)

    task_name: Mapped[str] = mapped_column(String(150), nullable=False)
    task_category: Mapped[str] = mapped_column(String(50), nullable=False)  # LAND_PREP, SOWING, IRRIGATION, FERTILIZATION, PLANT_PROTECTION, HARVEST
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="PLANNED", nullable=False)  # PLANNED, DUE, IN_PROGRESS, COMPLETED, SKIPPED, RESCHEDULED, CANCELLED

    weather_conflict_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conflict_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    execution_details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    calendar_def: Mapped[Optional["CropCalendarDefinition"]] = relationship("CropCalendarDefinition", back_populates="tasks")
    crop_season: Mapped["CropSeason"] = relationship("CropSeason")
    plot: Mapped["Plot"] = relationship("Plot")

    __table_args__ = (
        Index("ix_crop_tasks_season_due", "crop_season_id", "due_date"),
    )
