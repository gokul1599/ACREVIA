"""
ACREVIA - Farmer Collectives & FPO Domain Service (ACREVIA Collectives).
Pillar C: Organization registration, governance, membership roles, shared activities,
and privacy-preserving aggregate farm analytics (N >= 5 farms constraint).
"""

from collections import defaultdict
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.collective import (
    AgriculturalOrganization,
    OrganizationMembership,
    CollectiveActivity,
)
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.user import User
from backend.app.schemas.collective import (
    AgriculturalOrganizationCreate,
    CollectiveActivityCreate,
    CollectiveAggregateAnalytics,
)

logger = logging.getLogger(__name__)

MINIMUM_COHORT_SIZE = 5


class CollectivesService:

    @staticmethod
    def register_organization(
        db: Session,
        creator_user_id: str,
        data: AgriculturalOrganizationCreate,
    ) -> AgriculturalOrganization:
        org = AgriculturalOrganization(
            name=data.name.strip(),
            org_type=data.org_type,
            registration_number=data.registration_number.strip() if data.registration_number else None,
            state=data.state,
            district=data.district.strip(),
            description=data.description.strip() if data.description else None,
            contact_email=data.contact_email.strip() if data.contact_email else None,
            contact_phone=data.contact_phone.strip() if data.contact_phone else None,
            verification_status="APPLICATION_SUBMITTED",
        )
        db.add(org)
        db.flush()

        # Creator automatically becomes ORGANIZATION_ADMIN
        admin_membership = OrganizationMembership(
            organization_id=org.id,
            user_id=creator_user_id,
            org_role="ORGANIZATION_ADMIN",
            is_active=True,
        )
        db.add(admin_membership)
        db.commit()
        db.refresh(org)

        logger.info(
            "Registered organization %s (%s) by user %s",
            org.id,
            org.name,
            creator_user_id,
        )
        return org

    @staticmethod
    def get_organization(db: Session, org_id: str) -> Optional[AgriculturalOrganization]:
        stmt = (
            select(AgriculturalOrganization)
            .options(
                selectinload(AgriculturalOrganization.memberships),
                selectinload(AgriculturalOrganization.activities),
            )
            .where(AgriculturalOrganization.id == org_id)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def list_organizations(
        db: Session,
        district: Optional[str] = None,
        org_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AgriculturalOrganization]:
        stmt = select(AgriculturalOrganization).order_by(AgriculturalOrganization.created_at.desc())
        if district:
            stmt = stmt.where(AgriculturalOrganization.district == district)
        if org_type:
            stmt = stmt.where(AgriculturalOrganization.org_type == org_type)

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())

    @staticmethod
    def verify_organization(
        db: Session,
        org_id: str,
        admin_user: User,
        approve: bool = True,
    ) -> AgriculturalOrganization:
        user_roles = [r.id for r in admin_user.roles]
        if "ADMIN" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform administrators can verify agricultural organizations",
            )

        org = db.scalars(
            select(AgriculturalOrganization).where(AgriculturalOrganization.id == org_id)
        ).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agricultural organization not found",
            )

        org.verification_status = "APPROVED" if approve else "REJECTED"
        org.verified_by_user_id = admin_user.id
        db.commit()
        db.refresh(org)

        logger.info("Organization %s verification status updated to %s by admin %s", org_id, org.verification_status, admin_user.id)
        return org

    @staticmethod
    def join_organization(
        db: Session,
        org_id: str,
        user_id: str,
        org_role: str = "MEMBER",
    ) -> OrganizationMembership:
        org = db.scalars(
            select(AgriculturalOrganization).where(AgriculturalOrganization.id == org_id)
        ).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agricultural organization not found",
            )

        existing = db.scalars(
            select(OrganizationMembership).where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == user_id,
            )
        ).first()

        if existing:
            existing.is_active = True
            existing.org_role = org_role
            db.commit()
            db.refresh(existing)
            return existing

        membership = OrganizationMembership(
            organization_id=org_id,
            user_id=user_id,
            org_role=org_role,
            is_active=True,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def create_activity(
        db: Session,
        org_id: str,
        user_id: str,
        data: CollectiveActivityCreate,
    ) -> CollectiveActivity:
        # Check that user is an active member with authority
        membership = db.scalars(
            select(OrganizationMembership).where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active == True,
            )
        ).first()

        if not membership or membership.org_role not in ("ORGANIZATION_ADMIN", "GROUP_COORDINATOR", "ADVISOR"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization admins, coordinators, or advisors can create collective activities",
            )

        activity = CollectiveActivity(
            organization_id=org_id,
            created_by_user_id=user_id,
            activity_type=data.activity_type,
            title=data.title.strip(),
            description=data.description.strip(),
            target_date=data.target_date,
            status="PLANNED",
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    @staticmethod
    def list_activities(
        db: Session,
        org_id: str,
        user_id: str,
    ) -> List[CollectiveActivity]:
        # User must be member of organization
        membership = db.scalars(
            select(OrganizationMembership).where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active == True,
            )
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be a member of the organization to view collective activities",
            )

        stmt = (
            select(CollectiveActivity)
            .where(CollectiveActivity.organization_id == org_id)
            .order_by(CollectiveActivity.target_date.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_collective_analytics(
        db: Session,
        org_id: str,
        user_id: str,
    ) -> CollectiveAggregateAnalytics:
        # User must be an active member
        membership = db.scalars(
            select(OrganizationMembership).where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active == True,
            )
        ).first()

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Must be an active member of this organization to access aggregate metrics",
            )

        # Retrieve all member user IDs
        members = db.scalars(
            select(OrganizationMembership.user_id).where(
                OrganizationMembership.organization_id == org_id,
                OrganizationMembership.is_active == True,
            )
        ).all()
        member_user_ids = list(members)

        # Retrieve farms owned by these members
        farms = db.scalars(
            select(Farm).where(
                Farm.owner_id.in_(member_user_ids),
                Farm.is_archived == False,
            )
        ).all()
        distinct_farms_count = len(farms)

        # Privacy guardrail: enforce minimum cohort size of 5 farms
        if distinct_farms_count < MINIMUM_COHORT_SIZE:
            return CollectiveAggregateAnalytics(
                organization_id=org_id,
                total_member_farms=distinct_farms_count,
                aggregated_acreage=0.0,
                crop_distribution={},
                privacy_cohort_status="SUPPRESSED_INSUFFICIENT_COHORT",
                notes=(
                    f"Cohort size ({distinct_farms_count} farms) is below the privacy preservation threshold "
                    f"of {MINIMUM_COHORT_SIZE} farms. Aggregated acreage and crop distribution are suppressed."
                ),
            )

        # Calculate aggregated acreage safely across member farms
        aggregated_acreage = round(sum(f.total_acreage for f in farms), 2)

        # Calculate crop distribution across active seasons of member farms' plots
        farm_ids = [f.id for f in farms]
        plots = db.scalars(
            select(Plot).where(
                Plot.farm_id.in_(farm_ids),
                Plot.is_archived == False,
            )
        ).all()
        plot_ids = [p.id for p in plots]
        plot_acreage_map = {p.id: p.acreage for p in plots}

        crop_distribution: defaultdict[str, float] = defaultdict(float)
        if plot_ids:
            active_seasons = db.scalars(
                select(CropSeason).where(
                    CropSeason.plot_id.in_(plot_ids),
                    CropSeason.status == "ACTIVE",
                )
            ).all()

            for season in active_seasons:
                acreage = plot_acreage_map.get(season.plot_id, 0.0)
                crop_distribution[season.crop_id] += acreage

        # Round values for cleanliness
        formatted_distribution = {
            crop: round(acreage, 2)
            for crop, acreage in crop_distribution.items()
        }

        return CollectiveAggregateAnalytics(
            organization_id=org_id,
            total_member_farms=distinct_farms_count,
            aggregated_acreage=aggregated_acreage,
            crop_distribution=formatted_distribution,
            privacy_cohort_status="VALID_COHORT_GE_5",
            notes=(
                f"Aggregated across {distinct_farms_count} independent farms. "
                "Individual farmer financials, plot GPS boundaries, and personal records are strictly excluded."
            ),
        )
