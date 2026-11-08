"""
ACREVIA - Agricultural Knowledge Contribution Domain Service (ACREVIA Commons).
Pillar B: Governed knowledge submissions, expert review transitions, multilingual translation versions,
and handoff to production KrishiBrain RAG with source provenance.
"""

import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.commons_contribution import (
    KnowledgeContribution,
    ContributionReview,
    TranslationVersion,
)
from backend.app.models.knowledge_document import KnowledgeDocument
from backend.app.models.knowledge_source import KnowledgeSource
from backend.app.models.user import User
from backend.app.schemas.commons_contribution import (
    KnowledgeContributionCreate,
    ContributionReviewCreate,
    TranslationVersionCreate,
)

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"te", "en", "hi"}
SUPPORTED_CROPS = {"cotton", "rice", "chilli"}


class CommonsService:

    @staticmethod
    def submit_contribution(
        db: Session,
        user_id: str,
        data: KnowledgeContributionCreate,
    ) -> KnowledgeContribution:
        crop_id = data.crop_id.lower() if data.crop_id else None
        if crop_id and crop_id not in SUPPORTED_CROPS:
            logger.info("Custom crop %s submitted for knowledge contribution", crop_id)

        evidence_json = json.dumps(data.evidence_references or [])

        contribution = KnowledgeContribution(
            contributor_id=user_id,
            contribution_type=data.contribution_type,
            title=data.title.strip(),
            description=data.description.strip(),
            original_language=data.original_language,
            crop_id=crop_id,
            geographic_scope=data.geographic_scope,
            growth_stage=data.growth_stage,
            evidence_references_json=evidence_json,
            usage_permission=data.usage_permission,
            status="SUBMITTED",
            krishi_brain_ingested=False,
        )
        db.add(contribution)
        db.commit()
        db.refresh(contribution)
        logger.info("Knowledge contribution %s submitted by user %s", contribution.id, user_id)
        return contribution

    @staticmethod
    def get_contribution(db: Session, contribution_id: str) -> Optional[KnowledgeContribution]:
        stmt = (
            select(KnowledgeContribution)
            .options(
                selectinload(KnowledgeContribution.reviews),
                selectinload(KnowledgeContribution.translations),
            )
            .where(KnowledgeContribution.id == contribution_id)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def list_contributions(
        db: Session,
        status_filter: Optional[str] = None,
        crop_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[KnowledgeContribution]:
        stmt = (
            select(KnowledgeContribution)
            .options(
                selectinload(KnowledgeContribution.reviews),
                selectinload(KnowledgeContribution.translations),
            )
            .order_by(KnowledgeContribution.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(KnowledgeContribution.status == status_filter)
        if crop_id:
            stmt = stmt.where(KnowledgeContribution.crop_id == crop_id.lower())

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())

    @staticmethod
    def review_contribution(
        db: Session,
        contribution_id: str,
        expert_user: User,
        data: ContributionReviewCreate,
    ) -> ContributionReview:
        # Verify user is an agricultural expert or admin
        user_roles = [r.id for r in expert_user.roles]
        if "AGRICULTURAL_EXPERT" not in user_roles and "ADMIN" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified agricultural experts or administrators can review knowledge contributions",
            )

        contribution = db.scalars(
            select(KnowledgeContribution).where(KnowledgeContribution.id == contribution_id)
        ).first()
        if not contribution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge contribution not found",
            )

        review = ContributionReview(
            contribution_id=contribution.id,
            reviewer_id=expert_user.id,
            reviewer_role="EXPERT_AGRONOMIST" if "AGRICULTURAL_EXPERT" in user_roles else "MODERATOR",
            decision=data.decision,
            comments=data.comments,
            scientific_rating=data.scientific_rating,
            safety_assessment=data.safety_assessment,
        )
        db.add(review)

        # Update contribution status
        if data.decision == "APPROVE":
            contribution.status = "APPROVED"
            contribution.approved_by_user_id = expert_user.id
        elif data.decision == "REJECT":
            contribution.status = "REJECTED"
        elif data.decision == "REQUEST_REVISION":
            contribution.status = "AGRICULTURAL_REVIEW"

        db.commit()
        db.refresh(review)
        logger.info(
            "Contribution %s reviewed by expert %s: %s",
            contribution_id,
            expert_user.id,
            data.decision,
        )
        return review

    @staticmethod
    def create_translation(
        db: Session,
        contribution_id: str,
        user_id: str,
        data: TranslationVersionCreate,
    ) -> TranslationVersion:
        contribution = db.scalars(
            select(KnowledgeContribution).where(KnowledgeContribution.id == contribution_id)
        ).first()
        if not contribution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge contribution not found",
            )

        if data.target_language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target language must be one of: {list(SUPPORTED_LANGUAGES)}",
            )

        translation = TranslationVersion(
            contribution_id=contribution.id,
            target_language=data.target_language,
            translated_title=data.translated_title.strip(),
            translated_content=data.translated_content.strip(),
            is_native_reviewed=False,
            reviewer_id=None,
        )
        db.add(translation)
        db.commit()
        db.refresh(translation)
        logger.info(
            "Translation version created for contribution %s in language %s",
            contribution_id,
            data.target_language,
        )
        return translation

    @staticmethod
    def handoff_to_krishi_brain(
        db: Session,
        contribution_id: str,
        admin_or_expert_user: User,
    ) -> KnowledgeContribution:
        user_roles = [r.id for r in admin_or_expert_user.roles]
        if "ADMIN" not in user_roles and "AGRICULTURAL_EXPERT" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators or verified agricultural experts can ingest contributions into KrishiBrain",
            )

        contribution = CommonsService.get_contribution(db, contribution_id)
        if not contribution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge contribution not found",
            )

        if contribution.status not in ("APPROVED", "PUBLISHED"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot ingest contribution with status '{contribution.status}'. Must be APPROVED first.",
            )

        # Create or find production KnowledgeSource for ACREVIA Commons
        source = db.scalars(
            select(KnowledgeSource).where(KnowledgeSource.publisher_name == "ACREVIA Commons")
        ).first()
        if not source:
            source = KnowledgeSource(
                publisher_name="ACREVIA Commons",
                publisher_type="RESEARCH_COUNCIL",
                official_domain="commons.acrevia.ag",
                authority_level=0.9,
                licensing_status="GOVERNMENT_OPEN_ACCESS",
                approval_status="APPROVED",
            )
            db.add(source)
            db.flush()

        # Create production KnowledgeDocument in KrishiBrain
        doc = KnowledgeDocument(
            source_id=source.id,
            title=f"[ACREVIA Commons] {contribution.title}",
            canonical_url=f"/commons/contributions/{contribution.id}",
            document_type="TEXT",
            primary_language=contribution.original_language,
            crop_scope=contribution.crop_id or "cotton",
            region_scope=contribution.geographic_scope or "Telangana",
            status="APPROVED",
        )
        db.add(doc)
        db.flush()

        contribution.krishi_brain_ingested = True
        contribution.krishi_brain_doc_id = doc.id
        contribution.status = "PUBLISHED"
        db.commit()
        db.refresh(contribution)

        logger.info(
            "Contribution %s successfully handed off to KrishiBrain document %s",
            contribution.id,
            doc.id,
        )
        return contribution
