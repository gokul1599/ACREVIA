"""
ACREVIA - Farm Financial Ledger Models.
Provides decimal-safe farm expense recording, payment tracking, receipt linking, and immutable financial corrections.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class FarmExpense(Base, TimestampMixin):
    __tablename__ = "farm_expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=False)
    plot_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("plots.id", ondelete="SET NULL"), index=True, nullable=True)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="SET NULL"), index=True, nullable=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False)  # SEEDS, FERTILIZERS, PESTICIDES, LABOUR, MACHINERY, IRRIGATION, TRANSPORT, STORAGE, MISCELLANEOUS
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # KG, BAGS, LITRES, HOURS, DAYS

    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), default="PAID", nullable=False)  # PAID, PENDING, PARTIAL
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # CASH, UPI, BANK_TRANSFER, CREDIT_MERCHANT
    vendor_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    verification_state: Mapped[str] = mapped_column(String(30), default="UNVERIFIED", nullable=False)  # UNVERIFIED, PENDING_REVIEW, VERIFIED, FLAGGED

    # Relationships
    corrections: Mapped[List["FinancialCorrection"]] = relationship("FinancialCorrection", back_populates="expense", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_farm_expenses_farm_date", "farm_id", "transaction_date"),
        Index("ix_farm_expenses_season_category", "crop_season_id", "category"),
    )


class FinancialCorrection(Base):
    __tablename__ = "financial_corrections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    expense_id: Mapped[str] = mapped_column(String(36), ForeignKey("farm_expenses.id", ondelete="CASCADE"), index=True, nullable=False)
    previous_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    new_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    corrected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    expense: Mapped["FarmExpense"] = relationship("FarmExpense", back_populates="corrections")


class SaleTransaction(Base, TimestampMixin):
    __tablename__ = "sale_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_season_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_seasons.id", ondelete="CASCADE"), index=True, nullable=False)
    lot_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    buyer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    buyer_type: Mapped[str] = mapped_column(String(50), default="MANDI_TRADER", nullable=False)  # MANDI_TRADER, VILLAGE_AGGREGATOR, COOPERATIVE, CORPORATE_PROCESSOR
    quantity_sold: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="QUINTAL", nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deductions_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), default="PAID", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_sales_season_date", "crop_season_id", "sale_date"),
    )
