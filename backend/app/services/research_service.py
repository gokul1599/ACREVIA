"""
ACREVIA - Agricultural Research Hub Domain Service (ACREVIA Research Hub).
Pillar D: Research projects, purpose-specific consent, dataset splits, annotation tasks,
and disagreement tracking for research rigor.
"""

from datetime import datetime, timezone
import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.research_hub import (
    ResearchProject,
    ResearchConsent,
    DatasetContribution,
    AnnotationTask,
    AnnotationRecord,
)
from backend.app.models.user import User
from backend.app.schemas.research_hub import (
    ResearchProjectCreate,
    ResearchConsentCreate,
    DatasetContributionCreate,
    AnnotationTaskCreate,
    AnnotationRecordCreate,
)

logger = logging.getLogger(__name__)

VALID_SPLIT_TYPES = {"TRAIN", "VALIDATION", "TEST"}
VALID_CONSENT_SCOPES = {
    "OBSERVATIONS_ONLY",
    "ANNOTATED_IMAGES",
    "SENSOR_DATA",
    "HARVEST_METRICS",
    "FULL_RESEARCH",
}


class ResearchService:

    @staticmethod
    def create_project(
        db: Session,
        lead_researcher_id: str,
        data: ResearchProjectCreate,
    ) -> ResearchProject:
        crops_json = json.dumps(data.supported_crops or ["cotton", "rice", "chilli"])

        project = ResearchProject(
            title=data.title.strip(),
            lead_researcher_id=lead_researcher_id,
            institution_name=data.institution_name.strip(),
            research_objectives=data.research_objectives.strip(),
            supported_crops_json=crops_json,
            geographic_scope=data.geographic_scope,
            project_status="ACTIVE",
            publication_references_json="[]",
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        logger.info("Created research project %s (%s)", project.id, project.title)
        return project

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[ResearchProject]:
        stmt = (
            select(ResearchProject)
            .options(
                selectinload(ResearchProject.consents),
                selectinload(ResearchProject.datasets),
                selectinload(ResearchProject.tasks).selectinload(AnnotationTask.records),
            )
            .where(ResearchProject.id == project_id)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def list_projects(
        db: Session,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ResearchProject]:
        stmt = (
            select(ResearchProject)
            .options(
                selectinload(ResearchProject.consents),
                selectinload(ResearchProject.datasets),
                selectinload(ResearchProject.tasks),
            )
            .order_by(ResearchProject.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(ResearchProject.project_status == status_filter)

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())

    @staticmethod
    def grant_research_consent(
        db: Session,
        farmer_user_id: str,
        project_id: str,
        data: ResearchConsentCreate,
    ) -> ResearchConsent:
        project = db.scalars(select(ResearchProject).where(ResearchProject.id == project_id)).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research project not found",
            )

        if data.consent_scope not in VALID_CONSENT_SCOPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid consent scope. Must be one of: {list(VALID_CONSENT_SCOPES)}",
            )

        # Check existing consent
        existing = db.scalars(
            select(ResearchConsent).where(
                ResearchConsent.project_id == project_id,
                ResearchConsent.farmer_id == farmer_user_id,
            )
        ).first()

        if existing:
            existing.is_active = True
            existing.consent_scope = data.consent_scope
            existing.consent_version = data.consent_version
            existing.revoked_at = None
            db.commit()
            db.refresh(existing)
            logger.info("Updated research consent %s for farmer %s", existing.id, farmer_user_id)
            return existing

        consent = ResearchConsent(
            project_id=project_id,
            farmer_id=farmer_user_id,
            consent_scope=data.consent_scope,
            is_active=True,
            consent_version=data.consent_version,
            granted_at=datetime.now(timezone.utc),
        )
        db.add(consent)
        db.commit()
        db.refresh(consent)
        logger.info("Granted research consent %s for farmer %s", consent.id, farmer_user_id)
        return consent

    @staticmethod
    def revoke_research_consent(
        db: Session,
        consent_id: str,
        farmer_user: User,
    ) -> ResearchConsent:
        consent = db.scalars(
            select(ResearchConsent).where(ResearchConsent.id == consent_id)
        ).first()
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research consent record not found",
            )

        user_roles = [r.id for r in farmer_user.roles]
        if consent.farmer_id != farmer_user.id and "ADMIN" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only revoke your own research consent",
            )

        consent.is_active = False
        consent.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(consent)
        logger.info("Revoked research consent %s for farmer %s", consent.id, farmer_user.id)
        return consent

    @staticmethod
    def contribute_dataset(
        db: Session,
        contributor_id: str,
        data: DatasetContributionCreate,
    ) -> DatasetContribution:
        project = db.scalars(select(ResearchProject).where(ResearchProject.id == data.project_id)).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research project not found",
            )

        if data.split_type not in VALID_SPLIT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid split_type. Must be one of: {list(VALID_SPLIT_TYPES)}",
            )

        dataset = DatasetContribution(
            project_id=data.project_id,
            contributor_id=contributor_id,
            dataset_name=data.dataset_name.strip(),
            crop_id=data.crop_id.lower(),
            sample_count=data.sample_count,
            data_type=data.data_type,
            split_type=data.split_type,
            storage_uri=data.storage_uri.strip(),
            license=data.license,
            status="SUBMITTED",
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        logger.info("Dataset contribution %s added to project %s", dataset.id, data.project_id)
        return dataset

    @staticmethod
    def create_annotation_task(
        db: Session,
        data: AnnotationTaskCreate,
    ) -> AnnotationTask:
        project = db.scalars(select(ResearchProject).where(ResearchProject.id == data.project_id)).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research project not found",
            )

        task = AnnotationTask(
            project_id=data.project_id,
            assigned_expert_id=data.assigned_expert_id,
            task_type=data.task_type,
            entity_reference_id=data.entity_reference_id.strip(),
            status="PENDING",
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("Created annotation task %s for project %s", task.id, data.project_id)
        return task

    @staticmethod
    def submit_annotation_record(
        db: Session,
        task_id: str,
        annotator_id: str,
        data: AnnotationRecordCreate,
    ) -> AnnotationRecord:
        task = db.scalars(
            select(AnnotationTask)
            .options(selectinload(AnnotationTask.records))
            .where(AnnotationTask.id == task_id)
        ).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annotation task not found",
            )

        # Check existing records to detect inter-annotator disagreement
        disagreement_detected = False
        for existing in task.records:
            if existing.label_assigned.strip().lower() != data.label_assigned.strip().lower():
                disagreement_detected = True
                break

        record = AnnotationRecord(
            task_id=task_id,
            annotator_id=annotator_id,
            label_taxonomy_version=data.label_taxonomy_version,
            label_assigned=data.label_assigned.strip(),
            confidence_score=data.confidence_score,
            disagreement_flag=disagreement_detected,
            notes=data.notes.strip() if data.notes else None,
        )
        db.add(record)

        if disagreement_detected:
            task.status = "DISPUTED"
            logger.warning(
                "Annotation disagreement detected on task %s: conflicting label '%s'",
                task_id,
                data.label_assigned,
            )
        else:
            task.status = "COMPLETED"

        db.commit()
        db.refresh(record)
        return record
