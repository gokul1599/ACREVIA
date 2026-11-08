"""
ACREVIA - Agricultural Partner Ecosystem & Governed Onboarding Service.
Stage 14: Partner registration, verification lifecycle, integration adapters, and data sharing consent grants.
"""

from datetime import datetime, timedelta, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.interoperability import (
    IntegrationPartner,
    PartnerIntegration,
    DataSharingGrant,
)


class PartnerService:
    """
    Manages institutional partner onboarding, formal verification gates,
    adapter capabilities, and farmer consent grants.
    """

    @classmethod
    def register_partner(
        cls,
        db: Session,
        name: str,
        partner_type: str,
        contact_email: str,
        description: Optional[str] = None,
        website: Optional[str] = None,
        contact_phone: Optional[str] = None,
        legal_entity_number: Optional[str] = None,
    ) -> IntegrationPartner:
        partner = IntegrationPartner(
            name=name,
            partner_type=partner_type.upper(),
            description=description,
            website=website,
            contact_email=contact_email,
            contact_phone=contact_phone,
            legal_entity_number=legal_entity_number,
            verification_status="APPLICATION_SUBMITTED",
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)
        return partner

    @classmethod
    def verify_partner(
        cls,
        db: Session,
        partner_id: str,
        verification_status: str,
        verifier_user_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> IntegrationPartner:
        partner = db.get(IntegrationPartner, partner_id)
        if not partner:
            raise ValueError(f"Integration partner '{partner_id}' not found")

        partner.verification_status = verification_status.upper()
        partner.verification_notes = notes
        if verification_status.upper() == "VERIFIED":
            partner.verified_at = datetime.now(timezone.utc)
            partner.verified_by_user_id = verifier_user_id

        db.commit()
        db.refresh(partner)
        return partner

    @classmethod
    def list_partners(
        cls,
        db: Session,
        status: Optional[str] = None,
        partner_type: Optional[str] = None,
    ) -> List[IntegrationPartner]:
        stmt = select(IntegrationPartner)
        if status:
            stmt = stmt.where(IntegrationPartner.verification_status == status.upper())
        if partner_type:
            stmt = stmt.where(IntegrationPartner.partner_type == partner_type.upper())
        return db.scalars(stmt).all()

    @classmethod
    def get_partner(cls, db: Session, partner_id: str) -> Optional[IntegrationPartner]:
        return db.get(IntegrationPartner, partner_id)

    @classmethod
    def add_integration(
        cls,
        db: Session,
        partner_id: str,
        connector_type: str,
        display_name: str,
        capabilities: List[str],
        adapter_config: Optional[Dict[str, Any]] = None,
    ) -> PartnerIntegration:
        partner = db.get(IntegrationPartner, partner_id)
        if not partner:
            raise ValueError(f"Integration partner '{partner_id}' not found")

        integration = PartnerIntegration(
            partner_id=partner_id,
            connector_type=connector_type.upper(),
            display_name=display_name,
            capabilities_json=json.dumps(capabilities),
            adapter_config_json=json.dumps(adapter_config or {}),
            status="ACTIVE",
            health_status="HEALTHY",
            last_health_check_at=datetime.now(timezone.utc),
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration

    @classmethod
    def list_partner_integrations(cls, db: Session, partner_id: str) -> List[PartnerIntegration]:
        return db.scalars(select(PartnerIntegration).where(PartnerIntegration.partner_id == partner_id)).all()

    @classmethod
    def grant_consent(
        cls,
        db: Session,
        user_id: str,
        partner_id: str,
        purpose: str,
        farm_id: Optional[str] = None,
        plot_id: Optional[str] = None,
        data_categories: Optional[List[str]] = None,
        anonymize_pii: bool = True,
        redact_exact_gps: bool = True,
        expires_in_days: int = 90,
    ) -> DataSharingGrant:
        partner = db.get(IntegrationPartner, partner_id)
        if not partner:
            raise ValueError(f"Integration partner '{partner_id}' not found")

        categories = data_categories or ["FARM_PROFILE", "OBSERVATIONS"]
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        grant = DataSharingGrant(
            user_id=user_id,
            partner_id=partner_id,
            farm_id=farm_id,
            plot_id=plot_id,
            data_categories_json=json.dumps(categories),
            purpose=purpose,
            anonymize_pii=anonymize_pii,
            redact_exact_gps=redact_exact_gps,
            is_revoked=False,
            expires_at=expires_at,
        )
        db.add(grant)
        db.commit()
        db.refresh(grant)
        return grant

    @classmethod
    def revoke_consent(
        cls,
        db: Session,
        grant_id: str,
        user_id: str,
        reason: str,
    ) -> DataSharingGrant:
        grant = db.get(DataSharingGrant, grant_id)
        if not grant:
            raise ValueError(f"Data sharing grant '{grant_id}' not found")
        if grant.user_id != user_id:
            raise PermissionError("Access denied: You do not own this data sharing grant")

        grant.is_revoked = True
        grant.revoked_at = datetime.now(timezone.utc)
        grant.revocation_reason = reason
        db.commit()
        db.refresh(grant)
        return grant

    @classmethod
    def list_farmer_grants(cls, db: Session, user_id: str) -> List[DataSharingGrant]:
        return db.scalars(select(DataSharingGrant).where(DataSharingGrant.user_id == user_id)).all()
