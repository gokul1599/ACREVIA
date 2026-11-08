"""
ACREVIA - Agricultural Decision Intelligence API Endpoints (Pillar E: ACREVIA Decision).
Provides grounded multilingual recommendations, evidence audit trails, and farmer feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.models.decision_intelligence import DecisionRecord
from backend.app.schemas.decision_intelligence import (
    DecisionAnalyzeRequest,
    DecisionRecordResponse,
    EvidenceSourceItem,
    DecisionFeedbackCreate,
    DecisionFeedbackResponse,
)
from backend.app.security.dependencies import get_current_user, verify_farm_access
from backend.app.services.decision_service import DecisionService

router = APIRouter(prefix="/decisions", tags=["Decision Intelligence"])


@router.post("/analyze", response_model=DecisionRecordResponse, status_code=status.HTTP_200_OK)
def analyze_decision(
    data: DecisionAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Evaluates agricultural query against digital twin state and KrishiBrain evidence grounding.
    """
    plot = db.get(Plot, data.plot_id)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot '{data.plot_id}' not found.",
        )
    verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
    return DecisionService.analyze_decision(user=current_user, data=data, db=db)


@router.get("/{id}", response_model=DecisionRecordResponse)
def get_decision_record(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves full details and evidence sources of a previously generated decision record.
    """
    dec = db.get(DecisionRecord, id)
    if not dec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DecisionRecord '{id}' not found.",
        )
    plot = db.get(Plot, dec.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    return DecisionService._to_response(dec)


@router.post("/{id}/feedback", response_model=DecisionFeedbackResponse, status_code=status.HTTP_201_CREATED)
def record_decision_feedback(
    id: str,
    data: DecisionFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Records farmer feedback, adoption status, and observed real-world outcomes.
    """
    dec = db.get(DecisionRecord, id)
    if not dec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DecisionRecord '{id}' not found.",
        )
    plot = db.get(Plot, dec.plot_id)
    if plot:
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)

    return DecisionService.record_feedback(decision_id=id, data=data, db=db)
