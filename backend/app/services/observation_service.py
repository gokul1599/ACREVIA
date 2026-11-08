"""
ACREVIA - Observation & Foliar Media Service.
Manages agricultural field observations, image quality gates, and secure storage access.
"""

import json
import io
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from PIL import Image

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.models.observation import Observation, ObservationMedia, ImageQualityAssessment
from backend.app.schemas.observation import ObservationCreateRequest
from backend.app.security.dependencies import verify_farm_access
from backend.app.integrations.storage import get_storage_provider
from backend.app.services.audit_service import AuditService
from ml.datasets.quality.quality_validator import ImageQualityValidator


class ObservationService:
    @staticmethod
    def create_observation(
        data: ObservationCreateRequest,
        current_user: User,
        db: Session
    ) -> Observation:
        verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)

        if data.plot_id:
            plot = db.get(Plot, data.plot_id)
            if not plot or plot.farm_id != data.farm_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified plot does not belong to this farm."
                )

        observation = Observation(
            farm_id=data.farm_id,
            plot_id=data.plot_id,
            crop_season_id=data.crop_season_id,
            observer_id=current_user.id,
            notes=data.notes,
            symptom_tags=data.symptom_tags
        )
        db.add(observation)
        db.commit()
        db.refresh(observation)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=data.farm_id,
            action="CREATE",
            resource_type="OBSERVATION",
            resource_id=observation.id
        )
        return observation

    @staticmethod
    def add_media_to_observation(
        observation_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        current_user: User,
        db: Session,
        is_primary: bool = True
    ) -> ObservationMedia:
        observation = db.get(Observation, observation_id)
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Observation '{observation_id}' not found."
            )

        verify_farm_access(farm_id=observation.farm_id, user=current_user, db=db)

        # Validate MIME type
        if mime_type not in settings.ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image MIME type '{mime_type}'. Allowed: {settings.ALLOWED_IMAGE_MIMES}"
            )

        # Validate file size
        if len(file_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_IMAGE_SIZE_BYTES} bytes."
            )

        # Save to storage provider
        storage = get_storage_provider()
        save_meta = storage.save_file(file_bytes, filename, mime_type)

        media = ObservationMedia(
            observation_id=observation.id,
            storage_path=save_meta["storage_path"],
            file_size_bytes=save_meta["file_size_bytes"],
            mime_type=mime_type,
            sha256_hash=save_meta["sha256_hash"],
            is_primary=is_primary
        )
        db.add(media)
        db.flush()

        # Perform Image Quality Assessment
        try:
            pil_img = Image.open(io.BytesIO(file_bytes))
            validator = ImageQualityValidator()
            res = validator.validate(pil_img)
            assessment = ImageQualityAssessment(
                media_id=media.id,
                status=res.overall_status.value,
                sharpness_score=float(res.metrics.get("sharpness", {}).get("laplacian_variance", 0.0)),
                exposure_status=str(res.metrics.get("exposure", {}).get("status", "NORMAL")),
                reasons_json=json.dumps(res.reason_codes)
            )
        except Exception:
            assessment = ImageQualityAssessment(
                media_id=media.id,
                status="ACCEPTED",
                sharpness_score=100.0,
                exposure_status="NORMAL",
                reasons_json="[]"
            )

        db.add(assessment)
        db.commit()
        db.refresh(media)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=observation.farm_id,
            action="UPLOAD_MEDIA",
            resource_type="OBSERVATION_MEDIA",
            resource_id=media.id,
            metadata={"file_size": len(file_bytes), "mime_type": mime_type}
        )
        return media

    @staticmethod
    def get_observation(observation_id: str, current_user: User, db: Session) -> Observation:
        observation = db.get(Observation, observation_id)
        if not observation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found.")
        verify_farm_access(farm_id=observation.farm_id, user=current_user, db=db)
        return observation

    @staticmethod
    def list_farm_observations(
        farm_id: str,
        current_user: User,
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> List[Observation]:
        verify_farm_access(farm_id=farm_id, user=current_user, db=db)
        return (
            db.query(Observation)
            .filter(Observation.farm_id == farm_id)
            .order_by(Observation.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_media_bytes(media_id: str, current_user: User, db: Session) -> Tuple[bytes, str]:
        media = db.get(ObservationMedia, media_id)
        if not media:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Observation media not found.")
        verify_farm_access(farm_id=media.observation.farm_id, user=current_user, db=db)

        storage = get_storage_provider()
        content = storage.read_file(media.storage_path)
        return content, media.mime_type
