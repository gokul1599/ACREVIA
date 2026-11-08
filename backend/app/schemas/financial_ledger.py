"""
ACREVIA - Farm Financial Ledger Pydantic Schemas.
Pillar A: Expense recording, financial corrections, and crop sale transactions.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FarmExpenseCreate(BaseModel):
    farm_id: str
    plot_id: Optional[str] = None
    crop_season_id: Optional[str] = None
    category: str = "FERTILIZERS"  # SEEDS, FERTILIZERS, PESTICIDES, LABOUR, MACHINERY, IRRIGATION, TRANSPORT, STORAGE, MISCELLANEOUS
    description: str
    amount: Decimal
    currency: str = "INR"
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None  # KG, BAGS, LITRES, HOURS, DAYS
    transaction_date: date
    payment_status: str = "PAID"  # PAID, PENDING, PARTIAL
    payment_method: Optional[str] = "UPI"  # CASH, UPI, BANK_TRANSFER, CREDIT_MERCHANT
    vendor_name: Optional[str] = None
    receipt_url: Optional[str] = None
    created_by_user_id: Optional[str] = None


class FinancialCorrectionCreate(BaseModel):
    new_amount: Decimal
    reason: str


class FinancialCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    expense_id: str
    previous_amount: Decimal
    new_amount: Decimal
    reason: str
    corrected_by_user_id: Optional[str] = None
    corrected_at: datetime


class FarmExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    farm_id: str
    plot_id: Optional[str] = None
    crop_season_id: Optional[str] = None
    category: str
    description: str
    amount: Decimal
    currency: str
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    transaction_date: date
    payment_status: str
    payment_method: Optional[str] = None
    vendor_name: Optional[str] = None
    receipt_url: Optional[str] = None
    created_by_user_id: Optional[str] = None
    verification_state: str
    created_at: datetime
    updated_at: datetime
    corrections: List[FinancialCorrectionResponse] = Field(default_factory=list)


class SaleTransactionCreate(BaseModel):
    crop_season_id: str
    lot_id: Optional[str] = None
    buyer_name: str
    buyer_type: str = "MANDI_TRADER"  # MANDI_TRADER, VILLAGE_AGGREGATOR, COOPERATIVE, CORPORATE_PROCESSOR
    quantity_sold: Decimal
    unit: str = "QUINTAL"
    price_per_unit: Decimal
    gross_amount: Decimal
    deductions_amount: Decimal = Decimal("0.00")
    sale_date: date
    payment_status: str = "PAID"
    notes: Optional[str] = None


class SaleTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    crop_season_id: str
    lot_id: Optional[str] = None
    buyer_name: str
    buyer_type: str
    quantity_sold: Decimal
    unit: str
    price_per_unit: Decimal
    gross_amount: Decimal
    deductions_amount: Decimal
    net_amount: Decimal
    sale_date: date
    payment_status: str
    notes: Optional[str] = None
    created_at: datetime
