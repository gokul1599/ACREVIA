"""
ACREVIA - Regional Pulse & Intelligence Domain Service (ACREVIA Regional Pulse).
Pillar F: Privacy-preserving regional signal aggregation, minimum farm threshold (N >= 3),
and sensational outbreak claim suppression.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.regional_pulse import (
    RegionalSignal,
    RegionalSignalEvidence,
)
from backend.app.schemas.regional_pulse import RegionalSignalCreate

logger = logging.getLogger(__name__)

MINIMUM_DISTINCT_FARMS_THRESHOLD = 3

PANIC_KEYWORDS = [
    r"\boutbreak\b",
    r"\bepidemic\b",
    r"\bdevastation\b",
    r"\btotal\s+crop\s+loss\b",
    r"\bdisaster\b",
    r"\bcatastrophe\b",
    r"\bcrisis\b",
    r"\bpest\s+plague\b",
]


class RegionalPulseService:

    @staticmethod
    def sanitize_outbreak_language(text: str) -> tuple[str, bool]:
        suppressed = False
        sanitized = text
        for pattern in PANIC_KEYWORDS:
            if re.search(pattern, sanitized, flags=re.IGNORECASE):
                suppressed = True
                sanitized = re.sub(
                    pattern,
                    "elevated observation surge",
                    sanitized,
                    flags=re.IGNORECASE,
                )
        return sanitized, suppressed

    @staticmethod
    def aggregate_regional_signal(
        db: Session,
        data: RegionalSignalCreate,
        evidences: Optional[List[Dict[str, Any]]] = None,
    ) -> RegionalSignal:
        # Privacy & Reliability Guardrail 1: Enforce minimum distinct farms
        if data.distinct_farms_count < MINIMUM_DISTINCT_FARMS_THRESHOLD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Regional signal aggregation requires evidence from at least "
                    f"{MINIMUM_DISTINCT_FARMS_THRESHOLD} distinct farms to preserve farm anonymity "
                    f"and prevent isolated noise from generating false regional alarms."
                ),
            )

        # Anti-Panic Guardrail 2: Detect and suppress unverified sensational outbreak claims
        title_clean, suppressed_title = RegionalPulseService.sanitize_outbreak_language(data.signal_title)
        summary_clean, suppressed_summary = RegionalPulseService.sanitize_outbreak_language(data.signal_summary)
        outbreak_suppressed = suppressed_title or suppressed_summary

        # Only official state advisories or expert confirmed signals can bypass unvalidated status
        validation_status = data.validation_status
        if data.confidence_tier not in ("EXPERT_REVIEWED", "OFFICIAL_ADVISORY"):
            validation_status = "UNVALIDATED_OBSERVATION"

        signal = RegionalSignal(
            district=data.district.strip(),
            state=data.state,
            crop_id=data.crop_id.lower(),
            signal_category=data.signal_category,
            signal_title=title_clean.strip(),
            signal_summary=summary_clean.strip(),
            confidence_tier=data.confidence_tier,
            source_observation_count=data.source_observation_count,
            distinct_farms_count=data.distinct_farms_count,
            is_outbreak_claim_suppressed=outbreak_suppressed,
            validation_status=validation_status,
            recommended_action=data.recommended_action.strip(),
            observed_start_date=data.observed_start_date,
            observed_end_date=data.observed_end_date,
        )
        db.add(signal)
        db.flush()

        if evidences:
            for ev in evidences:
                evidence_item = RegionalSignalEvidence(
                    signal_id=signal.id,
                    evidence_type=ev.get("evidence_type", "OBSERVATION_REF"),
                    evidence_reference_id=ev.get("evidence_reference_id", "REF-001"),
                    evidence_notes=ev.get("evidence_notes"),
                )
                db.add(evidence_item)

        db.commit()
        db.refresh(signal)
        logger.info(
            "Aggregated regional signal %s for %s in %s (distinct_farms=%d, suppressed=%s)",
            signal.id,
            signal.crop_id,
            signal.district,
            signal.distinct_farms_count,
            signal.is_outbreak_claim_suppressed,
        )
        return signal

    @staticmethod
    def get_signal(db: Session, signal_id: str) -> Optional[RegionalSignal]:
        stmt = (
            select(RegionalSignal)
            .options(selectinload(RegionalSignal.evidences))
            .where(RegionalSignal.id == signal_id)
        )
        return db.scalars(stmt).first()

    @staticmethod
    def query_signals(
        db: Session,
        district: Optional[str] = None,
        crop_id: Optional[str] = None,
        confidence_tier: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RegionalSignal]:
        stmt = (
            select(RegionalSignal)
            .options(selectinload(RegionalSignal.evidences))
            .order_by(RegionalSignal.observed_end_date.desc())
        )
        if district:
            stmt = stmt.where(RegionalSignal.district == district)
        if crop_id:
            stmt = stmt.where(RegionalSignal.crop_id == crop_id.lower())
        if confidence_tier:
            stmt = stmt.where(RegionalSignal.confidence_tier == confidence_tier)

        return list(db.scalars(stmt.offset(offset).limit(limit)).all())
