"""
ACREVIA - ExpertConnect API Endpoints.
Provides agronomist credentialing, review queue triage, clinical dossiers, assessments, and immutable revisions.
"""

from typing import List, Optional
import json
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.expertconnect import (
    ExpertApplicationRequest,
    ExpertProfileResponse,
    AdminVerifyExpertRequest,
    ExpertCaseItemResponse,
    ExpertCaseDossierResponse,
    ExpertAssessmentCreateRequest,
    ExpertAssessmentRevisionRequest,
    ExpertAssessmentResponse,
    ExpertAssessmentRevisionResponse
)
from backend.app.security.dependencies import get_current_user, require_roles
from backend.app.security.permissions import SystemRole
from backend.app.services.expertconnect.expert_service import ExpertConnectService

router = APIRouter(prefix="/expertconnect", tags=["ExpertConnect - Human Agronomist Review Network"])


@router.post("/apply", response_model=ExpertProfileResponse, status_code=status.HTTP_201_CREATED)
def apply_for_expert_certification(
    data: ExpertApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits application for agricultural expert certification. Requires admin verification.
    """
    profile = ExpertConnectService.submit_application(user=current_user, data=data, db=db)
    specs = []
    dists = []
    try:
        specs = json.loads(profile.specializations_json)
        dists = json.loads(profile.districts_covered_json)
    except Exception:
        pass

    return ExpertProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        registration_number=profile.registration_number,
        highest_degree=profile.highest_degree,
        institution=profile.institution,
        specializations=specs,
        districts_covered=dists,
        verification_status=profile.verification_status,
        verified_at=profile.verified_at,
        rejection_reason=profile.rejection_reason
    )


@router.get("/profile/me", response_model=ExpertProfileResponse)
def get_my_expert_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the current authenticated user's expert certification profile.
    """
    profile = ExpertConnectService.get_my_profile(user=current_user, db=db)
    specs = []
    dists = []
    try:
        specs = json.loads(profile.specializations_json)
        dists = json.loads(profile.districts_covered_json)
    except Exception:
        pass

    return ExpertProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        registration_number=profile.registration_number,
        highest_degree=profile.highest_degree,
        institution=profile.institution,
        specializations=specs,
        districts_covered=dists,
        verification_status=profile.verification_status,
        verified_at=profile.verified_at,
        rejection_reason=profile.rejection_reason
    )


@router.post("/admin/verify/{profile_id}", response_model=ExpertProfileResponse)
def admin_verify_expert(
    profile_id: str,
    data: AdminVerifyExpertRequest,
    admin_user: User = Depends(require_roles(SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Platform Administrator verification of expert applicant.
    Grants AGRICULTURAL_EXPERT role upon approval.
    """
    profile = ExpertConnectService.admin_verify_expert(
        profile_id=profile_id,
        decision=data.decision,
        rejection_reason=data.rejection_reason,
        admin_user=admin_user,
        db=db
    )
    user = profile.user
    specs = []
    dists = []
    try:
        specs = json.loads(profile.specializations_json)
        dists = json.loads(profile.districts_covered_json)
    except Exception:
        pass

    return ExpertProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=user.full_name if user else "Expert",
        email=user.email if user else None,
        phone=user.phone if user else "",
        registration_number=profile.registration_number,
        highest_degree=profile.highest_degree,
        institution=profile.institution,
        specializations=specs,
        districts_covered=dists,
        verification_status=profile.verification_status,
        verified_at=profile.verified_at,
        rejection_reason=profile.rejection_reason
    )


@router.post("/cases/create-from-observation/{observation_id}", response_model=ExpertCaseItemResponse, status_code=status.HTTP_201_CREATED)
def create_case_from_observation(
    observation_id: str,
    priority: str = Query("ROUTINE", description="ROUTINE or URGENT"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Escalates an observation into a formal Expert Review Case.
    """
    case = ExpertConnectService.create_case(observation_id=observation_id, priority=priority, db=db)
    farm = case.farm
    return ExpertCaseItemResponse(
        id=case.id,
        observation_id=case.observation_id,
        farm_id=case.farm_id,
        farm_name=farm.name if farm else "Farm",
        district=farm.district if farm else "Telangana",
        plot_id=case.plot_id,
        crop_id=case.crop_id,
        priority=case.priority,
        status=case.status,
        assigned_expert_id=case.assigned_expert_id,
        assigned_expert_name=None,
        created_at=case.created_at
    )


@router.get("/cases", response_model=List[ExpertCaseItemResponse])
def list_expert_cases(
    status: Optional[str] = Query(None, description="QUEUED, ASSIGNED, IN_REVIEW, COMPLETED"),
    crop_id: Optional[str] = Query(None, description="cotton, rice, chilli"),
    priority: Optional[str] = Query(None, description="ROUTINE, URGENT"),
    current_user: User = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value, SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Lists consultation and review cases in the expert triage queue.
    """
    cases = ExpertConnectService.list_cases(
        status=status,
        crop_id=crop_id,
        priority=priority,
        current_user=current_user,
        db=db
    )
    return cases


@router.post("/cases/{case_id}/claim", response_model=ExpertCaseItemResponse)
def claim_case(
    case_id: str,
    current_user: User = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value, SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Certified expert claims a queued case atomically.
    """
    case = ExpertConnectService.claim_case(case_id=case_id, expert_user=current_user, db=db)
    farm = case.farm
    return ExpertCaseItemResponse(
        id=case.id,
        observation_id=case.observation_id,
        farm_id=case.farm_id,
        farm_name=farm.name if farm else "Farm",
        district=farm.district if farm else "Telangana",
        plot_id=case.plot_id,
        crop_id=case.crop_id,
        priority=case.priority,
        status=case.status,
        assigned_expert_id=case.assigned_expert_id,
        assigned_expert_name=current_user.full_name,
        created_at=case.created_at
    )


@router.get("/cases/{case_id}", response_model=ExpertCaseDossierResponse)
def get_case_dossier(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves full evidence dossier: foliar images, AI predictions, KrishiBrain knowledge citations, and weather context.
    """
    return ExpertConnectService.get_case_dossier(case_id=case_id, current_user=current_user, db=db)


@router.post("/cases/{case_id}/assess", response_model=ExpertAssessmentResponse, status_code=status.HTTP_201_CREATED)
def submit_expert_assessment(
    case_id: str,
    data: ExpertAssessmentCreateRequest,
    current_user: User = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value, SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Expert submits structured diagnostic finding and IPM-first management plan.
    """
    assessment = ExpertConnectService.submit_assessment(case_id=case_id, data=data, expert_user=current_user, db=db)
    diffs = []
    try:
        diffs = json.loads(assessment.differential_diagnoses_json)
    except Exception:
        pass

    expert_profile = db.query(User).filter_by(id=assessment.expert_id).first()
    exp_prof_model = db.query(User).filter_by(id=assessment.expert_id).first().owned_farms  # just user info
    prof_rec = assessment.expert

    return ExpertAssessmentResponse(
        id=assessment.id,
        case_id=assessment.case_id,
        expert_id=assessment.expert_id,
        expert_name=assessment.expert.full_name,
        expert_degree="Agronomist",
        expert_institution="Telangana State Agricultural Extension",
        confirmed_crop=assessment.confirmed_crop,
        primary_condition=assessment.primary_condition,
        differential_diagnoses=diffs,
        confidence_rating=assessment.confidence_rating,
        urgency_level=assessment.urgency_level,
        management_plan=assessment.management_plan,
        ipm_strategy=assessment.ipm_strategy,
        cibrc_advisories=assessment.cibrc_advisories,
        revision_count=assessment.revision_count,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at
    )


@router.put("/cases/{case_id}/assess", response_model=ExpertAssessmentResponse)
def revise_expert_assessment(
    case_id: str,
    data: ExpertAssessmentRevisionRequest,
    current_user: User = Depends(require_roles(SystemRole.AGRICULTURAL_EXPERT.value, SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Revises existing assessment, archiving the prior version immutably in ExpertAssessmentRevision.
    """
    assessment = ExpertConnectService.revise_assessment(case_id=case_id, data=data, expert_user=current_user, db=db)
    diffs = []
    try:
        diffs = json.loads(assessment.differential_diagnoses_json)
    except Exception:
        pass

    return ExpertAssessmentResponse(
        id=assessment.id,
        case_id=assessment.case_id,
        expert_id=assessment.expert_id,
        expert_name=assessment.expert.full_name,
        expert_degree="Agronomist",
        expert_institution="Telangana State Agricultural Extension",
        confirmed_crop=assessment.confirmed_crop,
        primary_condition=assessment.primary_condition,
        differential_diagnoses=diffs,
        confidence_rating=assessment.confidence_rating,
        urgency_level=assessment.urgency_level,
        management_plan=assessment.management_plan,
        ipm_strategy=assessment.ipm_strategy,
        cibrc_advisories=assessment.cibrc_advisories,
        revision_count=assessment.revision_count,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at
    )


@router.get("/cases/{case_id}/revisions", response_model=List[ExpertAssessmentRevisionResponse])
def get_case_assessment_revisions(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the immutable audit trail of all prior revisions for an assessment.
    """
    return ExpertConnectService.get_revisions(case_id=case_id, db=db)
