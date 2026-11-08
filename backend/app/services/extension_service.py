"""
ACREVIA - Agricultural Extension & Learning Domain Service (ACREVIA Extension).
Pillar E: Educational guides, university advisories, interactive training events,
and farmer feedback mechanisms.
"""

from datetime import datetime, timezone
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.extension_learning import (
    LearningResource,
    TrainingEvent,
    EventRegistration,
    LearningFeedback,
)
from backend.app.schemas.extension_learning import (
    LearningResourceCreate,
    TrainingEventCreate,
    LearningFeedbackCreate,
)

logger = logging.getLogger(__name__)


class ExtensionService:

    @staticmethod
    def publish_learning_resource(
        db: Session,
        creator_user_id: str,
        data: LearningResourceCreate,
    ) -> LearningResource:
        resource = LearningResource(
            title=data.title.strip(),
            content_body=data.content_body.strip(),
            resource_type=data.resource_type,
            creator_org_id=data.creator_org_id,
            creator_user_id=creator_user_id,
            crop_id=data.crop_id.lower() if data.crop_id else None,
            language=data.language,
            review_status="PUBLISHED",
            view_count=0,
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        logger.info("Published learning resource %s (%s)", resource.id, resource.title)
        return resource

    @staticmethod
    def get_learning_resource(
        db: Session,
        resource_id: str,
        increment_views: bool = True,
    ) -> Optional[LearningResource]:
        resource = db.scalars(
            select(LearningResource)
            .options(selectinload(LearningResource.feedback))
            .where(LearningResource.id == resource_id)
        ).first()

        if resource and increment_views:
            resource.view_count += 1
            db.commit()
            db.refresh(resource)

        return resource

    @staticmethod
    def list_learning_resources(
        db: Session,
        crop_id: Optional[str] = None,
        language: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[LearningResource]:
        stmt = select(LearningResource).order_by(LearningResource.created_at.desc())
        if crop_id:
            stmt = stmt.where(LearningResource.crop_id == crop_id.lower())
        if language:
            stmt = stmt.where(LearningResource.language == language)
        if resource_type:
            stmt = stmt.where(LearningResource.resource_type == resource_type)

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())

    @staticmethod
    def submit_feedback(
        db: Session,
        resource_id: str,
        user_id: str,
        data: LearningFeedbackCreate,
    ) -> LearningFeedback:
        resource = db.scalars(select(LearningResource).where(LearningResource.id == resource_id)).first()
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learning resource not found",
            )

        feedback = LearningFeedback(
            resource_id=resource_id,
            user_id=user_id,
            feedback_type=data.feedback_type,
            comments=data.comments.strip() if data.comments else None,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def create_training_event(
        db: Session,
        data: TrainingEventCreate,
    ) -> TrainingEvent:
        event = TrainingEvent(
            organizer_org_id=data.organizer_org_id,
            title=data.title.strip(),
            description=data.description.strip(),
            event_type=data.event_type,
            target_crop_id=data.target_crop_id.lower() if data.target_crop_id else None,
            district=data.district.strip(),
            scheduled_start=data.scheduled_start,
            scheduled_end=data.scheduled_end,
            is_online=data.is_online,
            meeting_link=data.meeting_link.strip() if data.meeting_link else None,
            max_capacity=data.max_capacity,
            status="SCHEDULED",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        logger.info("Created training event %s (%s)", event.id, event.title)
        return event

    @staticmethod
    def list_training_events(
        db: Session,
        district: Optional[str] = None,
        target_crop_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TrainingEvent]:
        stmt = (
            select(TrainingEvent)
            .options(selectinload(TrainingEvent.registrations))
            .order_by(TrainingEvent.scheduled_start.asc())
        )
        if district:
            stmt = stmt.where(TrainingEvent.district == district)
        if target_crop_id:
            stmt = stmt.where(TrainingEvent.target_crop_id == target_crop_id.lower())
        if status_filter:
            stmt = stmt.where(TrainingEvent.status == status_filter)

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())

    @staticmethod
    def register_for_event(
        db: Session,
        event_id: str,
        user_id: str,
    ) -> EventRegistration:
        event = db.scalars(select(TrainingEvent).where(TrainingEvent.id == event_id)).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training event not found",
            )

        existing = db.scalars(
            select(EventRegistration).where(
                EventRegistration.event_id == event_id,
                EventRegistration.user_id == user_id,
            )
        ).first()

        if existing:
            return existing

        # Capacity check
        current_count = db.scalar(
            select(func.count(EventRegistration.id)).where(
                EventRegistration.event_id == event_id,
                EventRegistration.attendance_status != "CANCELLED",
            )
        ) or 0

        if current_count >= event.max_capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Training event has reached maximum capacity ({event.max_capacity} attendees)",
            )

        registration = EventRegistration(
            event_id=event_id,
            user_id=user_id,
            attendance_status="REGISTERED",
        )
        db.add(registration)
        db.commit()
        db.refresh(registration)
        logger.info("User %s registered for training event %s", user_id, event_id)
        return registration
