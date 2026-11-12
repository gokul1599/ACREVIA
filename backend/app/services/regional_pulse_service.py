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
        from backend.app.models.farm import Farm
        from backend.app.models.observation import Observation
        from backend.app.models.risk_alert import RiskAlert

        # Check if evidences are provided either explicitly or via data model
        effective_evidences = evidences or getattr(data, "evidences", None)

        # Privacy & Reliability Guardrail 1: Enforce verified minimum distinct farms
        verified_distinct_farms = 0
        if effective_evidences:
            verified_farm_ids = set()
            for ev in effective_evidences:
                ref_id = ev.get("evidence_reference_id")
                ev_type = ev.get("evidence_type", "OBSERVATION_REF")
                if not ref_id:
                    continue
                if ev_type == "OBSERVATION_REF":
                    obs = db.get(Observation, ref_id)
                    if not obs or not obs.farm_id:
                        continue
                    farm = db.get(Farm, obs.farm_id)
                    if not farm or farm.is_archived:
                        continue
                    # Cross-region boundary check: farm district must match signal district
                    if farm.district.strip().lower() != data.district.strip().lower():
                        logger.warning(f"Excluding evidence {ref_id}: farm district '{farm.district}' mismatches signal district '{data.district}'")
                        continue
                    # Time window check: observation date must fall within signal window
                    obs_date = obs.created_at.date() if hasattr(obs, "created_at") and obs.created_at else None
                    if obs_date and (obs_date < data.observed_start_date or obs_date > data.observed_end_date):
                        logger.warning(f"Excluding evidence {ref_id}: observation date {obs_date} outside window [{data.observed_start_date}, {data.observed_end_date}]")
                        continue
                    verified_farm_ids.add(farm.id)

                elif ev_type in ("RISKCAST_ALERT", "RISK_ALERT"):
                    alert = db.get(RiskAlert, ref_id)
                    if not alert or not alert.farm_id:
                        continue
                    farm = db.get(Farm, alert.farm_id)
                    if not farm or farm.is_archived:
                        continue
                    if farm.district.strip().lower() != data.district.strip().lower():
                        logger.warning(f"Excluding alert evidence {ref_id}: farm district '{farm.district}' mismatches signal district '{data.district}'")
                        continue
                    alert_date = alert.created_at.date() if hasattr(alert, "created_at") and alert.created_at else None
                    if alert_date and (alert_date < data.observed_start_date or alert_date > data.observed_end_date):
                        logger.warning(f"Excluding alert evidence {ref_id}: alert date {alert_date} outside window [{data.observed_start_date}, {data.observed_end_date}]")
                        continue
                    verified_farm_ids.add(farm.id)

            verified_distinct_farms = len(verified_farm_ids)
            if verified_distinct_farms < MINIMUM_DISTINCT_FARMS_THRESHOLD:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Regional signal aggregation requires verified evidence from at least "
                        f"{MINIMUM_DISTINCT_FARMS_THRESHOLD} distinct farms matching district '{data.district}' "
                        f"and observation window [{data.observed_start_date} to {data.observed_end_date}] "
                        f"(found {verified_distinct_farms}) to preserve farm anonymity."
                    ),
                )
        else:
            # Unlinked requests: client assertions of distinct_farms_count without evidence are strictly rejected
            if data.confidence_tier != "OFFICIAL_ADVISORY":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Regional signal aggregation requires verified evidence records linking at least "
                        f"{MINIMUM_DISTINCT_FARMS_THRESHOLD} distinct farms. Client-supplied assertions without evidence are rejected."
                    ),
                )
            # Official state advisories without plot telemetry have count 0
            verified_distinct_farms = 0

        final_distinct_count = verified_distinct_farms

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
            distinct_farms_count=final_distinct_count,
            is_outbreak_claim_suppressed=outbreak_suppressed,
            validation_status=validation_status,
            recommended_action=data.recommended_action.strip(),
            observed_start_date=data.observed_start_date,
            observed_end_date=data.observed_end_date,
        )
        db.add(signal)
        db.flush()

        if effective_evidences:
            for ev in effective_evidences:
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

    @staticmethod
    def revalidate_signal_provenance(db: Session, signal_id: str) -> bool:
        """
        Revalidates distinct farm count from linked evidence records post-publication.
        If underlying evidence records were deleted or altered such that distinct farms < 3,
        suppresses signal status to 'SUPPRESSED_INSUFFICIENT_PROVENANCE'.
        """
        from backend.app.models.farm import Farm
        from backend.app.models.observation import Observation
        from backend.app.models.risk_alert import RiskAlert

        signal = RegionalPulseService.get_signal(db, signal_id)
        if not signal:
            return False

        if signal.confidence_tier == "OFFICIAL_ADVISORY":
            return True

        verified_farms = set()
        for ev in signal.evidences:
            if ev.evidence_type == "OBSERVATION_REF":
                obs = db.get(Observation, ev.evidence_reference_id)
                if obs and obs.farm_id:
                    farm = db.get(Farm, obs.farm_id)
                    if farm and not farm.is_archived and farm.district.strip().lower() == signal.district.strip().lower():
                        verified_farms.add(farm.id)
            elif ev.evidence_type in ("RISKCAST_ALERT", "RISK_ALERT"):
                alert = db.get(RiskAlert, ev.evidence_reference_id)
                if alert and alert.farm_id:
                    farm = db.get(Farm, alert.farm_id)
                    if farm and not farm.is_archived and farm.district.strip().lower() == signal.district.strip().lower():
                        verified_farms.add(farm.id)

        current_count = len(verified_farms)
        signal.distinct_farms_count = current_count
        if current_count < MINIMUM_DISTINCT_FARMS_THRESHOLD:
            signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
            logger.warning(
                f"Signal {signal_id} suppressed: verified distinct farms dropped to {current_count} (< {MINIMUM_DISTINCT_FARMS_THRESHOLD})"
            )
            db.commit()
            return False

        db.commit()
        return True
