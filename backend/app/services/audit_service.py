"""
ACREVIA - Audit Logging Service.
Records immutable activity trails for all farm mutations and AI diagnostic requests.
"""

import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.governance import AuditLog
from backend.app.core.logging import logger


class AuditService:
    @staticmethod
    def stage_activity(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        farm_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Stages an append-only audit log entry in the current session transaction
        without calling db.commit(), preserving transaction ownership for the caller.
        """
        meta_str = json.dumps(metadata) if metadata else None
        entry = AuditLog(
            user_id=user_id,
            farm_id=farm_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            metadata_json=meta_str
        )
        db.add(entry)
        logger.info(f"AUDIT STAGED: action={action} resource={resource_type}:{resource_id} user={user_id} farm={farm_id}")
        return entry

    @staticmethod
    def record_activity(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        farm_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """
        Creates an append-only audit log record and commits immediately.
        """
        entry = AuditService.stage_activity(
            db=db,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            farm_id=farm_id,
            metadata=metadata,
            ip_address=ip_address
        )
        db.commit()
        db.refresh(entry)
        logger.info(f"AUDIT COMMITTED: action={action} resource={resource_type}:{resource_id} user={user_id} farm={farm_id}")
        return entry

    record_action = record_activity


audit_service = AuditService()
