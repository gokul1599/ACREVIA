"""
ACREVIA - Crop Season Economics & Loss Evidence API Endpoints.
Pillar F: Cost of cultivation, gross revenues, unit margins, and insurance evidence packages.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.crop_economics import (
    EconomicsSummaryResponse,
)
from backend.app.schemas.evidence_package import (
    CropLossEvidencePackageCreate,
    CropLossEvidencePackageResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.economics_service import EconomicsService

router = APIRouter(prefix="/economics", tags=["Crop Season Economics"])


@router.get("/seasons/{crop_season_id}", response_model=EconomicsSummaryResponse, status_code=status.HTTP_200_OK)
def get_season_economics(
    crop_season_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Computes cost of cultivation, net realization, unit margins, and data completeness scoring.
    """
    return EconomicsService.calculate_crop_season_economics(db, crop_season_id=crop_season_id)


@router.post("/evidence-package", response_model=CropLossEvidencePackageResponse, status_code=status.HTTP_201_CREATED)
def create_loss_evidence_package(
    data: CropLossEvidencePackageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates a cryptographically hashed evidence bundle for PMFBY insurance claims and state disaster relief.
    """
    verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)
    return EconomicsService.generate_crop_loss_evidence_package(db, data)
