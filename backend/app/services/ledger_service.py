"""
ACREVIA - Farm Financial Ledger Service.
Provides expense tracking, receipt attachment, immutable corrections, and sales transactions.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.financial_ledger import FarmExpense, FinancialCorrection, SaleTransaction
from backend.app.schemas.financial_ledger import (
    FarmExpenseCreate,
    FinancialCorrectionCreate,
    SaleTransactionCreate,
)


class LedgerService:
    @staticmethod
    def create_expense(db: Session, data: FarmExpenseCreate) -> FarmExpense:
        farm = db.get(Farm, data.farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{data.farm_id}' not found.",
            )

        if data.plot_id:
            plot = db.get(Plot, data.plot_id)
            if not plot or plot.farm_id != data.farm_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plot '{data.plot_id}' does not belong to farm '{data.farm_id}'.",
                )

        if data.crop_season_id:
            season = db.get(CropSeason, data.crop_season_id)
            if not season:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"CropSeason '{data.crop_season_id}' not found.",
                )

        if data.amount <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expense amount must be strictly greater than zero.",
            )

        expense = FarmExpense(
            farm_id=data.farm_id,
            plot_id=data.plot_id,
            crop_season_id=data.crop_season_id,
            category=data.category.upper(),
            description=data.description,
            amount=data.amount,
            currency=data.currency,
            quantity=data.quantity,
            unit=data.unit,
            transaction_date=data.transaction_date,
            payment_status=data.payment_status.upper(),
            payment_method=data.payment_method.upper() if data.payment_method else None,
            vendor_name=data.vendor_name,
            receipt_url=data.receipt_url,
            created_by_user_id=data.created_by_user_id,
            verification_state="PENDING_REVIEW" if data.receipt_url else "UNVERIFIED",
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def get_expenses(
        db: Session,
        farm_id: str,
        crop_season_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[FarmExpense]:
        query = select(FarmExpense).where(FarmExpense.farm_id == farm_id)
        if crop_season_id:
            query = query.where(FarmExpense.crop_season_id == crop_season_id)
        if category:
            query = query.where(FarmExpense.category == category.upper())
        query = query.order_by(FarmExpense.transaction_date.desc()).limit(limit).offset(offset)
        return list(db.scalars(query).all())

    @staticmethod
    def correct_expense(
        db: Session,
        expense_id: str,
        data: FinancialCorrectionCreate,
        user_id: Optional[str] = None,
    ) -> FarmExpense:
        expense = db.get(FarmExpense, expense_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense '{expense_id}' not found.",
            )

        if data.new_amount <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrected amount must be strictly greater than zero.",
            )

        if not data.reason or len(data.reason.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An audit reason of at least 5 characters is required for financial corrections.",
            )

        correction = FinancialCorrection(
            expense_id=expense.id,
            previous_amount=expense.amount,
            new_amount=data.new_amount,
            reason=data.reason.strip(),
            corrected_by_user_id=user_id,
        )
        db.add(correction)

        expense.amount = data.new_amount
        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def create_sale_transaction(db: Session, data: SaleTransactionCreate) -> SaleTransaction:
        season = db.get(CropSeason, data.crop_season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropSeason '{data.crop_season_id}' not found.",
            )

        if data.quantity_sold <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity sold must be greater than zero.",
            )

        if data.price_per_unit <= Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price per unit must be greater than zero.",
            )

        calculated_gross = data.quantity_sold * data.price_per_unit
        net_amount = calculated_gross - data.deductions_amount
        if net_amount < Decimal("0.00"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deductions cannot exceed the gross transaction value.",
            )

        sale = SaleTransaction(
            crop_season_id=data.crop_season_id,
            lot_id=data.lot_id,
            buyer_name=data.buyer_name,
            buyer_type=data.buyer_type.upper(),
            quantity_sold=data.quantity_sold,
            unit=data.unit.upper(),
            price_per_unit=data.price_per_unit,
            gross_amount=calculated_gross,
            deductions_amount=data.deductions_amount,
            net_amount=net_amount,
            sale_date=data.sale_date,
            payment_status=data.payment_status.upper(),
            notes=data.notes,
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale

    @staticmethod
    def get_sales(db: Session, crop_season_id: str) -> List[SaleTransaction]:
        query = select(SaleTransaction).where(SaleTransaction.crop_season_id == crop_season_id).order_by(SaleTransaction.sale_date.desc())
        return list(db.scalars(query).all())
