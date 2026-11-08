"""
ACREVIA - Farm, Membership & Plot Models.
Core multi-tenant domain boundary establishing farm data isolation.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), default="Telangana", nullable=False)
    district: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., Warangal, Khammam, Nalgonda
    mandal: Mapped[str] = mapped_column(String(50), nullable=False)
    village: Mapped[str] = mapped_column(String(50), nullable=False)
    total_acreage: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_farms")
    memberships: Mapped[List["FarmMembership"]] = relationship("FarmMembership", back_populates="farm", cascade="all, delete-orphan")
    plots: Mapped[List["Plot"]] = relationship("Plot", back_populates="farm", cascade="all, delete-orphan")
    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="farm", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_farms_district_mandal", "district", "mandal"),
    )


class FarmMembership(Base, TimestampMixin):
    __tablename__ = "farm_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role_in_farm: Mapped[str] = mapped_column(String(50), default="WORKER", nullable=False)  # OWNER, MANAGER, WORKER, AGRONOMIST_ADVISOR

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="farm_memberships")

    __table_args__ = (
        Index("uq_farm_user_membership", "farm_id", "user_id", unique=True),
    )


class Plot(Base, TimestampMixin):
    __tablename__ = "plots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    soil_type: Mapped[str] = mapped_column(String(50), default="BLACK_COTTON", nullable=False)  # BLACK_COTTON, RED_CHALKA, ALLUVIAL
    irrigation_source: Mapped[str] = mapped_column(String(50), default="BOREWELL", nullable=False)  # BOREWELL, CANAL, RAINFED, DRIP
    acreage: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    boundary_geojson: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="plots")
    seasons: Mapped[List["CropSeason"]] = relationship("CropSeason", back_populates="plot", cascade="all, delete-orphan")
    plants: Mapped[List["Plant"]] = relationship("Plant", back_populates="plot", cascade="all, delete-orphan")


class Plant(Base, TimestampMixin):
    __tablename__ = "plants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plot_id: Mapped[str] = mapped_column(String(36), ForeignKey("plots.id", ondelete="CASCADE"), index=True, nullable=False)
    tag_code: Mapped[str] = mapped_column(String(50), nullable=False)
    crop_id: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="plants")
