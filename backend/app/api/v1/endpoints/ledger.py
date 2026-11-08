"""
ACREVIA - Farm Financial Ledger API Endpoints.
Pillar A: Farm expenses, receipts, corrections, and crop sale transactions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.financial_ledger import (
    FarmExpenseCreate,
    FarmExpenseResponse,
    FinancialCorrectionCreate,
    SaleTransactionCreate,
    SaleTransactionResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.ledger_service import LedgerService

router = APIRouter(prefix="/ledger", tags=["Farm Financial Ledger"])


@router.post("/expenses", response_model=FarmExpenseResponse, status_code=status.HTTP_201_CREATED)
def record_expense(
    data: FarmExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)
    data.created_by_user_id = current_user.id
    return LedgerService.create_expense(db, data)


@router.get("/expenses", response_model=List[FarmExpenseResponse], status_code=status.HTTP_200_OK)
def list_expenses(
    farm_id: str = Query(..., description="ID of the farm"),
    crop_season_id: Optional[str] = Query(None, description="Optional crop season ID filter"),
    category: Optional[str] = Query(None, description="Optional expense category filter"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    verify_farm_access(farm_id=farm_id, user=current_user, db=db)
    return LedgerService.get_expenses(db, farm_id=farm_id, crop_season_id=crop_season_id, category=category, limit=limit, offset=offset)


@router.post("/expenses/{expense_id}/correct", response_model=FarmExpenseResponse, status_code=status.HTTP_200_OK)
def correct_expense(
    expense_id: str,
    data: FinancialCorrectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LedgerService.correct_expense(db, expense_id=expense_id, data=data, user_id=current_user.id)


@router.post("/sales", response_model=SaleTransactionResponse, status_code=status.HTTP_201_CREATED)
def record_sale(
    data: SaleTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LedgerService.create_sale_transaction(db, data)


@router.get("/sales", response_model=List[SaleTransactionResponse], status_code=status.HTTP_200_OK)
def list_sales(
    crop_season_id: str = Query(..., description="Crop season ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LedgerService.get_sales(db, crop_season_id=crop_season_id)
