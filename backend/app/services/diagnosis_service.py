"""
ACREVIA - AI Diagnosis & Expert Review Lifecycle Service.
Orchestrates foliar pathology inference, uncertainty metrics, and human agronomist review.
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.observation import Observation, ObservationMedia
from backend.app.models.diagnosis import (
    DiagnosisRequest,
    Prediction,
    PredictionCandidate,
    ExpertReview,
)
from backend.app.schemas.diagnosis import DiagnosisCreateRequest, ExpertReviewCreateRequest
from backend.app.security.dependencies import verify_farm_access
from backend.app.security.permissions import SystemRole
from backend.app.integrations.storage import get_storage_provider
from backend.app.integrations.ml_client import ml_client
from backend.app.services.audit_service import AuditService
from backend.app.core.logging import logger


class DiagnosisService:
    @staticmethod
    async def process_diagnosis(
        data: DiagnosisCreateRequest,
        current_user: User,
        db: Session
    ) -> DiagnosisRequest:
        observation = db.get(Observation, data.observation_id)
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Observation '{data.observation_id}' not found."
            )

        verify_farm_access(farm_id=observation.farm_id, user=current_user, db=db)

        # Resolve media
        media: Optional[ObservationMedia] = None
        if data.media_id:
            media = db.get(ObservationMedia, data.media_id)
            if not media or media.observation_id != observation.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified media does not belong to this observation."
                )
        else:
            if observation.media:
                media = next((m for m in observation.media if m.is_primary), observation.media[0])

        if not media:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot request diagnosis on an observation without uploaded foliar media."
            )

        # Create DiagnosisRequest record in CREATED state
        diag_request = DiagnosisRequest(
            observation_id=observation.id,
            media_id=media.id,
            status="PROCESSING",
            requested_at=datetime.now(timezone.utc)
        )
        db.add(diag_request)
        db.commit()
        db.refresh(diag_request)

        # Read media bytes from storage
        storage = get_storage_provider()
        try:
            image_bytes = storage.read_file(media.storage_path)
        except Exception as e:
            diag_request.status = "FAILED"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read media from storage: {e}"
            )

        # Call Stage 3 ML Inference Microservice
        ml_resp = await ml_client.submit_diagnosis(
            image_bytes=image_bytes,
            crop_type=data.crop_type,
            filename=media.storage_path,
            language=data.language
        )

        now_utc = datetime.now(timezone.utc)

        if "predictions" in ml_resp and ml_resp["predictions"]:
            # Successful ML prediction returned
            pred_meta = ml_resp.get("metadata", {})
            decision_state = ml_resp.get("decision_state", "HIGH_CONFIDENCE_DIAGNOSIS")
            model_ver = pred_meta.get("model_version", "MobileNetV3-Stage3-v1.0")

            prediction = Prediction(
                diagnosis_request_id=diag_request.id,
                model_version=model_ver,
                decision_state=decision_state,
                top_confidence=float(ml_resp.get("top_confidence", 0.0)),
                normalized_entropy=float(pred_meta.get("normalized_entropy", 0.0)) if "normalized_entropy" in pred_meta else None,
                prediction_margin=float(pred_meta.get("prediction_margin", 0.0)) if "prediction_margin" in pred_meta else None,
                cibrc_advisory=ml_resp.get("cibrc_advisory", "Consult local Krishi Vigyan Kendra (KVK) for CIBRC-approved IPM guidance.")
            )
            db.add(prediction)
            db.flush()

            for rank_idx, candidate in enumerate(ml_resp["predictions"], start=1):
                cand = PredictionCandidate(
                    prediction_id=prediction.id,
                    rank=rank_idx,
                    class_id=candidate.get("class_id", f"unknown_{rank_idx}"),
                    display_name_en=candidate.get("display_name_en", candidate.get("display_name", "")),
                    display_name_te=candidate.get("display_name_te", ""),
                    display_name_hi=candidate.get("display_name_hi", ""),
                    pathogen_or_cause=candidate.get("pathogen_or_cause"),
                    calibrated_prob=float(candidate.get("calibrated_prob", candidate.get("confidence", 0.0)))
                )
                db.add(cand)

            if decision_state in ["EXPERT_REVIEW_REQUIRED", "AMBIGUOUS_SYMPTOMS", "OUT_OF_DISTRIBUTION"]:
                diag_request.status = "NEEDS_REVIEW"
            else:
                diag_request.status = "COMPLETED"

            diag_request.completed_at = now_utc

        else:
            # Fallback when inference service is in offline evaluation mode or degraded
            logger.warning(f"Inference service returned fallback: {ml_resp}")
            prediction = Prediction(
                diagnosis_request_id=diag_request.id,
                model_version="ACREVIA-Fallback-v1.0",
                decision_state="EXPERT_REVIEW_REQUIRED",
                top_confidence=0.50,
                normalized_entropy=0.85,
                prediction_margin=0.05,
                cibrc_advisory="Automated classification queued for agronomist review. Please verify with local KVK agronomist."
            )
            db.add(prediction)
            db.flush()

            fallback_cand = PredictionCandidate(
                prediction_id=prediction.id,
                rank=1,
                class_id=f"{data.crop_type}_suspected_pathology",
                display_name_en=f"Suspected {data.crop_type.capitalize()} Foliar Anomaly",
                display_name_te=f"{data.crop_type} ఆకు తెగులు అనుమానం",
                display_name_hi=f"{data.crop_type} पत्ती रोग संदेह",
                pathogen_or_cause="Pending Agronomist Verification",
                calibrated_prob=0.50
            )
            db.add(fallback_cand)

            diag_request.status = "NEEDS_REVIEW"
            diag_request.completed_at = now_utc

        db.commit()
        db.refresh(diag_request)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=observation.farm_id,
            action="REQUEST_DIAGNOSIS",
            resource_type="DIAGNOSIS_REQUEST",
            resource_id=diag_request.id,
            metadata={"status": diag_request.status}
        )
        return diag_request

    @staticmethod
    def get_diagnosis(diagnosis_id: str, current_user: User, db: Session) -> DiagnosisRequest:
        diag = db.get(DiagnosisRequest, diagnosis_id)
        if not diag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis request not found.")
        verify_farm_access(farm_id=diag.observation.farm_id, user=current_user, db=db)
        return diag

    @staticmethod
    def submit_expert_review(
        diagnosis_id: str,
        data: ExpertReviewCreateRequest,
        current_user: User,
        db: Session
    ) -> ExpertReview:
        # Check system role: user must be AGRICULTURAL_EXPERT or ADMIN
        user_roles = [r.id for r in current_user.roles]
        if SystemRole.AGRICULTURAL_EXPERT.value not in user_roles and SystemRole.ADMIN.value not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered Agricultural Experts or Administrators can validate diagnoses."
            )

        diag = db.get(DiagnosisRequest, diagnosis_id)
        if not diag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnosis request not found.")

        # Check if expert review already exists
        review = db.query(ExpertReview).filter(ExpertReview.diagnosis_request_id == diag.id).first()
        now_utc = datetime.now(timezone.utc)

        if not review:
            review = ExpertReview(
                diagnosis_request_id=diag.id,
                expert_id=current_user.id,
                status=data.status,
                verified_class_id=data.verified_class_id,
                expert_notes=data.expert_notes,
                reviewed_at=now_utc
            )
            db.add(review)
        else:
            review.expert_id = current_user.id
            review.status = data.status
            review.verified_class_id = data.verified_class_id
            review.expert_notes = data.expert_notes
            review.reviewed_at = now_utc

        diag.status = "COMPLETED"
        db.commit()
        db.refresh(review)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=diag.observation.farm_id,
            action="EXPERT_REVIEW",
            resource_type="EXPERT_REVIEW",
            resource_id=review.id,
            metadata={"status": data.status, "verified_class": data.verified_class_id}
        )
        return review
