"""
ACREVIA - Multi-Source Evidence Fusion REST API (Pillar D: Acrevia Fusion).
Synthesizes satellite canopy vigor, IoT root telemetry, CropVision diagnoses,
and farm operations into conflict-resolved multilingual explanations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.fusion import (
    FusionExplanationResponse,
    MultilingualText,
    FusionContradiction
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.fusion_service import FusionService

router = APIRouter(prefix="/fusion", tags=["Acrevia Fusion"])


@router.get("/plots/{plot_id}/assessment", response_model=FusionExplanationResponse)
def get_plot_fusion_assessment(
    plot_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluates multi-source evidence fusion for a cultivation plot.
    Detects contradictions, resolves conflicting signals, and outputs
    plain-language explanations in Telugu, English, and Hindi.
    """
    explanation = FusionService.evaluate_plot_fusion(db=db, plot_id=plot_id)
    return FusionExplanationResponse(
        id=explanation.id,
        plot_id=explanation.plot_id,
        evaluation_timestamp=explanation.evaluation_timestamp,
        overall_vigor_status=explanation.overall_vigor_status,
        primary_stress_driver=explanation.primary_stress_driver,
        evidence_sources=explanation.evidence_sources_json,
        contradictions_detected=[
            FusionContradiction(
                conflict_type=c["conflict_type"],
                description=c["description"],
                resolution=c["resolution"]
            )
            for c in explanation.contradictions_detected_json
        ],
        farmer_explanation=MultilingualText(
            en=explanation.farmer_explanation_en,
            te=explanation.farmer_explanation_te,
            hi=explanation.farmer_explanation_hi
        ),
        epistemic_qualifications=explanation.epistemic_qualifications_json
    )
