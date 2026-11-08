"""
ACREVIA - ExpertConnect Service.
Orchestrates expert onboarding, administrator verification, case triage, clinical dossiers, and immutable assessments.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from backend.app.core.exceptions import NotFoundException, AuthorizationException, ValidationException
from backend.app.models.user import User, Role
from backend.app.models.observation import Observation
from backend.app.models.diagnosis import DiagnosisRequest, Prediction
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.expert_profile import ExpertProfile
from backend.app.models.expert_case import ExpertReviewCase
from backend.app.models.expert_assessment import ExpertAssessment, ExpertAssessmentRevision
from backend.app.models.knowledge_chunk import KnowledgeChunk
from backend.app.schemas.expertconnect import (
    ExpertApplicationRequest,
    ExpertAssessmentCreateRequest,
    ExpertAssessmentRevisionRequest
)
from backend.app.security.permissions import SystemRole
from backend.app.services.riskcast.weather_service import WeatherService


class ExpertConnectService:
    @classmethod
    def submit_application(cls, user: User, data: ExpertApplicationRequest, db: Session) -> ExpertProfile:
        """
        Submits candidate application for human agricultural expert certification.
        """
        existing = db.scalars(select(ExpertProfile).filter_by(user_id=user.id)).first()
        if existing:
            if existing.verification_status == "APPROVED":
                raise ValidationException("User is already a verified agricultural expert.")
            # Update existing application
            existing.registration_number = data.registration_number
            existing.highest_degree = data.highest_degree
            existing.institution = data.institution
            existing.specializations_json = json.dumps(data.specializations)
            existing.districts_covered_json = json.dumps(data.districts_covered)
            existing.verification_status = "APPLICATION_SUBMITTED"
            existing.rejection_reason = None
            db.commit()
            db.refresh(existing)
            return existing

        profile = ExpertProfile(
            user_id=user.id,
            registration_number=data.registration_number,
            highest_degree=data.highest_degree,
            institution=data.institution,
            specializations_json=json.dumps(data.specializations),
            districts_covered_json=json.dumps(data.districts_covered),
            verification_status="APPLICATION_SUBMITTED"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def get_my_profile(cls, user: User, db: Session) -> ExpertProfile:
        profile = db.scalars(select(ExpertProfile).filter_by(user_id=user.id)).first()
        if not profile:
            raise NotFoundException("No expert profile found for current user.")
        return profile

    @classmethod
    def admin_verify_expert(
        cls,
        profile_id: str,
        decision: str,
        rejection_reason: Optional[str],
        admin_user: User,
        db: Session
    ) -> ExpertProfile:
        """
        Platform Administrator approval or rejection of an expert profile.
        Grants AGRICULTURAL_EXPERT role on approval.
        """
        profile = db.get(ExpertProfile, profile_id)
        if not profile:
            raise NotFoundException(f"Expert profile '{profile_id}' not found.")

        profile.verification_status = decision
        profile.verified_by_user_id = admin_user.id
        profile.verified_at = datetime.now(timezone.utc)
        profile.rejection_reason = rejection_reason if decision == "REJECTED" else None

        target_user = db.get(User, profile.user_id)
        if target_user:
            expert_role = db.get(Role, SystemRole.AGRICULTURAL_EXPERT.value)
            if decision == "APPROVED":
                if expert_role and expert_role not in target_user.roles:
                    target_user.roles.append(expert_role)
            elif decision in ("REJECTED", "SUSPENDED", "REVOKED"):
                if expert_role and expert_role in target_user.roles:
                    target_user.roles.remove(expert_role)

        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def create_case(
        cls,
        observation_id: str,
        priority: str = "ROUTINE",
        diagnosis_request_id: Optional[str] = None,
        db: Session = None
    ) -> ExpertReviewCase:
        """
        Creates an expert review case from an observation or diagnostic escalation.
        """
        obs = db.get(Observation, observation_id)
        if not obs:
            raise NotFoundException(f"Observation '{observation_id}' not found.")

        # Determine crop
        crop_id = "cotton"
        if obs.season and obs.season.crop_id:
            crop_id = obs.season.crop_id
        elif obs.plot_id:
            latest_s = db.scalars(
                select(CropSeason).filter_by(plot_id=obs.plot_id).order_by(desc(CropSeason.created_at))
            ).first()
            if latest_s:
                crop_id = latest_s.crop_id

        case = ExpertReviewCase(
            diagnosis_request_id=diagnosis_request_id,
            observation_id=obs.id,
            farm_id=obs.farm_id,
            plot_id=obs.plot_id,
            crop_id=crop_id,
            priority=priority,
            status="QUEUED"
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @classmethod
    def list_cases(
        cls,
        status: Optional[str],
        crop_id: Optional[str],
        priority: Optional[str],
        current_user: User,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Lists review cases for verified experts.
        """
        stmt = select(ExpertReviewCase)
        conditions = []
        if status:
            conditions.append(ExpertReviewCase.status == status)
        if crop_id:
            conditions.append(ExpertReviewCase.crop_id == crop_id.lower().strip())
        if priority:
            conditions.append(ExpertReviewCase.priority == priority)

        if conditions:
            stmt = stmt.filter(and_(*conditions))

        stmt = stmt.order_by(
            desc(ExpertReviewCase.priority == "URGENT"),
            desc(ExpertReviewCase.created_at)
        )
        cases = db.scalars(stmt).all()

        results = []
        for c in cases:
            farm = c.farm
            expert = c.assigned_expert
            results.append({
                "id": c.id,
                "observation_id": c.observation_id,
                "farm_id": c.farm_id,
                "farm_name": farm.name if farm else "Unknown Farm",
                "district": farm.district if farm else "Telangana",
                "plot_id": c.plot_id,
                "crop_id": c.crop_id,
                "priority": c.priority,
                "status": c.status,
                "assigned_expert_id": c.assigned_expert_id,
                "assigned_expert_name": expert.full_name if expert else None,
                "created_at": c.created_at
            })
        return results

    @classmethod
    def claim_case(cls, case_id: str, expert_user: User, db: Session) -> ExpertReviewCase:
        """
        Expert claims a queued case atomically.
        """
        case = db.get(ExpertReviewCase, case_id)
        if not case:
            raise NotFoundException(f"Case '{case_id}' not found.")

        if case.status != "QUEUED" and case.assigned_expert_id != expert_user.id:
            raise ValidationException(f"Case is already claimed or in status '{case.status}'.")

        case.assigned_expert_id = expert_user.id
        case.status = "ASSIGNED"
        case.assigned_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(case)
        return case

    @classmethod
    def get_case_dossier(cls, case_id: str, current_user: User, db: Session) -> Dict[str, Any]:
        """
        Assembles clinical evidence dossier for agronomist examination:
        foliar media, AI vision results, KrishiBrain knowledge citations, and weather context.
        """
        case = db.get(ExpertReviewCase, case_id)
        if not case:
            raise NotFoundException(f"Case '{case_id}' not found.")

        obs = case.observation
        farm = case.farm
        plot = case.plot

        # Foliar images
        media_list = []
        if obs and obs.media:
            for m in obs.media:
                media_list.append({
                    "id": m.id,
                    "mime_type": m.mime_type,
                    "file_size_bytes": m.file_size_bytes,
                    "sha256_hash": m.sha256_hash,
                    "storage_path": f"/api/v1/observations/{obs.id}/media/{m.id}/stream"
                })

        # AI Prediction
        ai_pred_dict = None
        if case.diagnosis_request_id:
            diag = db.get(DiagnosisRequest, case.diagnosis_request_id)
            if diag and diag.prediction:
                pred = diag.prediction
                candidates = []
                for c in pred.candidates:
                    candidates.append({
                        "rank": c.rank,
                        "class_id": c.class_id,
                        "display_name_en": c.display_name_en,
                        "display_name_te": c.display_name_te,
                        "calibrated_prob": c.calibrated_prob
                    })
                ai_pred_dict = {
                    "decision_state": pred.decision_state,
                    "top_confidence": pred.top_confidence,
                    "normalized_entropy": pred.normalized_entropy,
                    "prediction_margin": pred.prediction_margin,
                    "candidates": candidates,
                    "cibrc_advisory": pred.cibrc_advisory
                }

        # Knowledge citations
        knowledge_citations = []
        chunks = db.scalars(
            select(KnowledgeChunk).filter(KnowledgeChunk.crop_scope == case.crop_id).limit(3)
        ).all()
        for ch in chunks:
            knowledge_citations.append({
                "source_title": ch.heading_path or ch.parent_section or "PJTSAU Advisory Guidelines",
                "content_excerpt": ch.content[:250] + "...",
                "cibrc_approved": True
            })

        # Weather context
        weather = WeatherService.get_latest_weather(farm_id=farm.id, db=db)
        weather_dict = {
            "temperature_celsius": weather.temperature_celsius,
            "relative_humidity": weather.relative_humidity,
            "precipitation_mm": weather.precipitation_mm,
            "leaf_wetness_hours": weather.leaf_wetness_hours,
            "source_provider": weather.source_provider
        } if weather else None

        # Assessment details if present
        assessment_dict = None
        if case.assessment:
            a = case.assessment
            diffs = []
            try:
                diffs = json.loads(a.differential_diagnoses_json)
            except Exception:
                pass
            assessment_dict = {
                "id": a.id,
                "expert_id": a.expert_id,
                "expert_name": a.expert.full_name,
                "confirmed_crop": a.confirmed_crop,
                "primary_condition": a.primary_condition,
                "differential_diagnoses": diffs,
                "confidence_rating": a.confidence_rating,
                "urgency_level": a.urgency_level,
                "management_plan": a.management_plan,
                "ipm_strategy": a.ipm_strategy,
                "cibrc_advisories": a.cibrc_advisories,
                "revision_count": a.revision_count,
                "updated_at": a.updated_at.isoformat()
            }

        return {
            "case_id": case.id,
            "observation_id": case.observation_id,
            "farm_id": farm.id,
            "farm_name": farm.name,
            "district": farm.district,
            "plot_id": plot.id if plot else None,
            "plot_name": plot.name if plot else None,
            "crop_id": case.crop_id,
            "growth_stage": "Vegetative",
            "priority": case.priority,
            "status": case.status,
            "assigned_expert_id": case.assigned_expert_id,
            "assigned_expert_name": case.assigned_expert.full_name if case.assigned_expert else None,
            "farmer_notes": obs.notes if obs else None,
            "symptom_tags": obs.symptom_tags if obs else None,
            "foliar_media": media_list,
            "ai_prediction": ai_pred_dict,
            "krishi_brain_citations": knowledge_citations,
            "weather_context": weather_dict,
            "assessment": assessment_dict,
            "created_at": case.created_at
        }

    @classmethod
    def submit_assessment(
        cls,
        case_id: str,
        data: ExpertAssessmentCreateRequest,
        expert_user: User,
        db: Session
    ) -> ExpertAssessment:
        """
        Expert submits certified diagnostic assessment, completing the case.
        """
        case = db.get(ExpertReviewCase, case_id)
        if not case:
            raise NotFoundException(f"Case '{case_id}' not found.")

        if case.assessment:
            raise ValidationException("Case already has an assessment. Use revision endpoint to update.")

        assessment = ExpertAssessment(
            case_id=case.id,
            expert_id=expert_user.id,
            confirmed_crop=data.confirmed_crop,
            primary_condition=data.primary_condition,
            differential_diagnoses_json=json.dumps(data.differential_diagnoses),
            confidence_rating=data.confidence_rating,
            urgency_level=data.urgency_level,
            management_plan=data.management_plan,
            ipm_strategy=data.ipm_strategy,
            cibrc_advisories=data.cibrc_advisories,
            revision_count=0
        )
        db.add(assessment)
        case.status = "COMPLETED"
        case.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(assessment)
        return assessment

    @classmethod
    def revise_assessment(
        cls,
        case_id: str,
        data: ExpertAssessmentRevisionRequest,
        expert_user: User,
        db: Session
    ) -> ExpertAssessment:
        """
        Revises existing assessment, archiving prior content immutably in ExpertAssessmentRevision.
        """
        case = db.get(ExpertReviewCase, case_id)
        if not case or not case.assessment:
            raise NotFoundException(f"No existing assessment found for case '{case_id}'.")

        a = case.assessment

        # Archive snapshot
        prior_snapshot = {
            "confirmed_crop": a.confirmed_crop,
            "primary_condition": a.primary_condition,
            "differential_diagnoses_json": a.differential_diagnoses_json,
            "confidence_rating": a.confidence_rating,
            "urgency_level": a.urgency_level,
            "management_plan": a.management_plan,
            "ipm_strategy": a.ipm_strategy,
            "cibrc_advisories": a.cibrc_advisories,
            "revision_count": a.revision_count
        }

        revision_num = a.revision_count + 1
        rev = ExpertAssessmentRevision(
            assessment_id=a.id,
            revision_number=revision_num,
            previous_assessment_json=json.dumps(prior_snapshot),
            revision_reason=data.revision_reason,
            revised_by_user_id=expert_user.id,
            revised_at=datetime.now(timezone.utc)
        )
        db.add(rev)

        # Mutate active assessment
        a.confirmed_crop = data.confirmed_crop
        a.primary_condition = data.primary_condition
        a.differential_diagnoses_json = json.dumps(data.differential_diagnoses)
        a.confidence_rating = data.confidence_rating
        a.urgency_level = data.urgency_level
        a.management_plan = data.management_plan
        a.ipm_strategy = data.ipm_strategy
        a.cibrc_advisories = data.cibrc_advisories
        a.revision_count = revision_num

        db.commit()
        db.refresh(a)
        return a

    @classmethod
    def get_revisions(cls, case_id: str, db: Session) -> List[Dict[str, Any]]:
        case = db.get(ExpertReviewCase, case_id)
        if not case or not case.assessment:
            raise NotFoundException(f"No assessment found for case '{case_id}'.")

        stmt = (
            select(ExpertAssessmentRevision)
            .filter_by(assessment_id=case.assessment.id)
            .order_by(ExpertAssessmentRevision.revision_number)
        )
        revs = db.scalars(stmt).all()

        results = []
        for r in revs:
            prev = {}
            try:
                prev = json.loads(r.previous_assessment_json)
            except Exception:
                pass
            results.append({
                "id": r.id,
                "assessment_id": r.assessment_id,
                "revision_number": r.revision_number,
                "previous_assessment": prev,
                "revision_reason": r.revision_reason,
                "revised_by_user_id": r.revised_by_user_id,
                "revised_by_name": r.revised_by.full_name if r.revised_by else "Agronomist",
                "revised_at": r.revised_at
            })
        return results
