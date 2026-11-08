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
        Creates an append-only audit log record.
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
        db.commit()
        db.refresh(entry)
        logger.info(f"AUDIT: action={action} resource={resource_type}:{resource_id} user={user_id} farm={farm_id}")
        return entry

    record_action = record_activity


audit_service = AuditService()
