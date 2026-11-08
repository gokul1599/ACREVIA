"""
ACREVIA - Consent & DPDP Governance Service.
Tracks user consent records under Digital Personal Data Protection Act compliance.
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.governance import ConsentRecord
from backend.app.schemas.consent import ConsentCreateRequest
from backend.app.services.audit_service import AuditService


class ConsentService:
    @staticmethod
    def record_consent(user: User, data: ConsentCreateRequest, db: Session) -> ConsentRecord:
        now_utc = datetime.now(timezone.utc)
        record = (
            db.query(ConsentRecord)
            .filter(
                ConsentRecord.user_id == user.id,
                ConsentRecord.consent_type == data.consent_type
            )
            .first()
        )

        if not record:
            record = ConsentRecord(
                user_id=user.id,
                consent_type=data.consent_type,
                is_granted=data.is_granted,
                policy_version=data.policy_version,
                granted_at=now_utc if data.is_granted else None,
                revoked_at=now_utc if not data.is_granted else None
            )
            db.add(record)
        else:
            record.is_granted = data.is_granted
            record.policy_version = data.policy_version
            if data.is_granted:
                record.granted_at = now_utc
                record.revoked_at = None
            else:
                record.revoked_at = now_utc

        db.commit()
        db.refresh(record)

        AuditService.record_action(
            db=db,
            user_id=user.id,
            action="UPDATE_CONSENT",
            resource_type="CONSENT_RECORD",
            resource_id=record.id,
            metadata={"type": data.consent_type, "granted": data.is_granted}
        )
        return record

    @staticmethod
    def get_user_consents(user: User, db: Session) -> List[ConsentRecord]:
        return db.query(ConsentRecord).filter(ConsentRecord.user_id == user.id).all()
