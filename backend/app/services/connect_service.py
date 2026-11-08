"""
ACREVIA - Agricultural Collaboration & Community Service (ACREVIA Connect).
Pillar A: Community directory, discussions, expert response badging, helpful voting, and reporting.
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.community import (
    Community,
    CommunityMembership,
    CommunityPost,
    CommunityComment,
    CommunityReport,
)
from backend.app.schemas.community import (
    CommunityCreate,
    CommunityPostCreate,
    CommunityCommentCreate,
    CommunityReportCreate,
)

DEFAULT_COMMUNITIES = [
    {
        "name": "Telangana Cotton Cultivators",
        "slug": "telangana-cotton",
        "description": "Collaborative space for cotton growers in Warangal, Adilabad, and Khammam discussing HDPS, boll management, and IPM.",
        "category": "CROP",
        "crop_id": "cotton",
        "district": "Warangal",
    },
    {
        "name": "Telangana Paddy & Rice Systems",
        "slug": "telangana-paddy",
        "description": "Discussion forum for direct-seeded rice (DSR), alternate wetting and drying (AWD), and pest management.",
        "category": "CROP",
        "crop_id": "rice",
        "district": "Karimnagar",
    },
    {
        "name": "Red Chilli Growers Circle",
        "slug": "red-chilli-circle",
        "description": "Exchange on Teja and Guntur varieties, thrips management, drying yards, and cold storage planning.",
        "category": "CROP",
        "crop_id": "chilli",
        "district": "Khammam",
    },
    {
        "name": "Soil Health & Micro-Irrigation",
        "slug": "soil-and-water",
        "description": "Sustainable farming techniques, vermicompost, borewell recharge, and drip scheduling.",
        "category": "PRACTICE",
        "crop_id": None,
        "district": None,
    },
]


class ConnectService:
    @classmethod
    def seed_default_communities(cls, db: Session):
        existing = db.scalars(select(Community)).first()
        if not existing:
            for c in DEFAULT_COMMUNITIES:
                db.add(Community(**c))
            db.commit()

    @classmethod
    def list_communities(
        cls,
        db: Session,
        category: Optional[str] = None,
        crop_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Community]:
        cls.seed_default_communities(db)
        query = select(Community)
        if category:
            query = query.where(Community.category == category.upper())
        if crop_id:
            query = query.where(Community.crop_id == crop_id.lower())
        query = query.order_by(Community.name.asc()).limit(limit).offset(offset)
        return list(db.scalars(query).all())

    @classmethod
    def join_community(cls, db: Session, community_id: str, user_id: str) -> CommunityMembership:
        community = db.get(Community, community_id)
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Community '{community_id}' not found.",
            )

        existing = db.scalar(
            select(CommunityMembership).where(
                CommunityMembership.community_id == community_id,
                CommunityMembership.user_id == user_id,
            )
        )
        if existing:
            return existing

        membership = CommunityMembership(
            community_id=community_id,
            user_id=user_id,
            role="MEMBER",
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @classmethod
    def create_post(
        cls,
        db: Session,
        community_id: str,
        user_id: str,
        data: CommunityPostCreate,
    ) -> CommunityPost:
        community = db.get(Community, community_id)
        if not community:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Community '{community_id}' not found.",
            )

        post = CommunityPost(
            community_id=community_id,
            author_id=user_id,
            post_type=data.post_type.upper(),
            title=data.title.strip(),
            content=data.content.strip(),
            language=data.language.lower(),
            crop_id=data.crop_id.lower() if data.crop_id else community.crop_id,
            growth_stage=data.growth_stage,
            visibility=data.visibility.upper(),
            moderation_status="APPROVED",
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @classmethod
    def list_posts(
        cls,
        db: Session,
        community_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CommunityPost]:
        query = (
            select(CommunityPost)
            .where(
                CommunityPost.community_id == community_id,
                CommunityPost.moderation_status.in_(["APPROVED", "PENDING"]),
            )
            .order_by(desc(CommunityPost.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(db.scalars(query).all())

    @classmethod
    def add_comment(
        cls,
        db: Session,
        post_id: str,
        user: User,
        data: CommunityCommentCreate,
    ) -> CommunityComment:
        post = db.get(CommunityPost, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post '{post_id}' not found.",
            )

        user_role_ids = [r.id for r in user.roles]
        is_expert = "AGRICULTURAL_EXPERT" in user_role_ids or "ADMIN" in user_role_ids

        comment = CommunityComment(
            post_id=post_id,
            author_id=user.id,
            content=data.content.strip(),
            is_expert_reply=is_expert,
            moderation_status="APPROVED",
        )
        db.add(comment)

        if is_expert:
            post.is_expert_reviewed = True

        db.commit()
        db.refresh(comment)
        return comment

    @classmethod
    def vote_helpful(cls, db: Session, post_id: str, user_id: str) -> CommunityPost:
        post = db.get(CommunityPost, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post '{post_id}' not found.",
            )
        post.helpful_count += 1
        db.commit()
        db.refresh(post)
        return post

    @classmethod
    def report_content(
        cls,
        db: Session,
        user_id: str,
        data: CommunityReportCreate,
    ) -> CommunityReport:
        if not data.post_id and not data.comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or comment_id must be provided for a report.",
            )

        report = CommunityReport(
            post_id=data.post_id,
            comment_id=data.comment_id,
            reported_by_user_id=user_id,
            reason_category=data.reason_category.upper(),
            details=data.details,
            status="PENDING",
        )
        db.add(report)

        # Flag post for moderation review
        if data.post_id:
            post = db.get(CommunityPost, data.post_id)
            if post:
                post.moderation_status = "FLAGGED"

        db.commit()
        db.refresh(report)
        return report
