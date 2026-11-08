"""
ACREVIA - Climate Resilience Service (Pillar C).
Provides 30-year climatological baselines, assesses crop-stage hazard vulnerability,
and generates actionable adaptation scenario comparisons.
"""

from datetime import datetime, timezone
import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.climate_resilience import (
    ClimateBaseline,
    ClimateExposureAssessment,
    ClimateAdaptationScenario,
)
from backend.app.models.farm import Plot
from backend.app.models.crop import Crop
from backend.app.schemas.climate_resilience import (
    ClimateExposureAssessmentRequest,
    ClimateExposureAssessmentResponse,
    ClimateAdaptationScenarioResponse,
    ClimateBaselineResponse,
)

logger = logging.getLogger(__name__)

# Canonical 30-year monthly normals (1991-2020) for Telangana agro-climatic zone
DEFAULT_TELANGANA_NORMALS = [
    {"month": 1, "rainfall": 7.5, "tmax": 30.2, "tmin": 16.5, "heat_days": 0.0, "dry_freq": 0.0},
    {"month": 2, "rainfall": 9.2, "tmax": 33.4, "tmin": 19.1, "heat_days": 0.0, "dry_freq": 0.0},
    {"month": 3, "rainfall": 14.8, "tmax": 37.1, "tmin": 22.8, "heat_days": 3.0, "dry_freq": 0.0},
    {"month": 4, "rainfall": 22.5, "tmax": 40.2, "tmin": 25.9, "heat_days": 8.0, "dry_freq": 0.0},
    {"month": 5, "rainfall": 31.0, "tmax": 41.8, "tmin": 28.2, "heat_days": 14.0, "dry_freq": 0.0},
    {"month": 6, "rainfall": 142.0, "tmax": 35.8, "tmin": 25.4, "heat_days": 2.0, "dry_freq": 0.5},
    {"month": 7, "rainfall": 248.5, "tmax": 31.2, "tmin": 23.9, "heat_days": 0.0, "dry_freq": 0.8},
    {"month": 8, "rainfall": 215.0, "tmax": 30.5, "tmin": 23.4, "heat_days": 0.0, "dry_freq": 0.9},
    {"month": 9, "rainfall": 168.2, "tmax": 31.5, "tmin": 23.2, "heat_days": 0.0, "dry_freq": 0.7},
    {"month": 10, "rainfall": 94.0, "tmax": 32.1, "tmin": 21.6, "heat_days": 0.0, "dry_freq": 0.3},
    {"month": 11, "rainfall": 24.5, "tmax": 30.8, "tmin": 18.2, "heat_days": 0.0, "dry_freq": 0.1},
    {"month": 12, "rainfall": 6.8, "tmax": 29.8, "tmin": 15.6, "heat_days": 0.0, "dry_freq": 0.0},
]


class ClimateService:

    @staticmethod
    def get_district_baselines(db: Session, district_code: str) -> List[ClimateBaselineResponse]:
        stmt = (
            select(ClimateBaseline)
            .where(ClimateBaseline.district_code == district_code)
            .order_by(ClimateBaseline.month.asc())
        )
        records = list(db.execute(stmt).scalars().all())

        if not records:
            # Seed or return canonical Telangana normals
            for item in DEFAULT_TELANGANA_NORMALS:
                baseline = ClimateBaseline(
                    district_code=district_code,
                    month=item["month"],
                    normal_rainfall_mm=item["rainfall"],
                    normal_tmax_celsius=item["tmax"],
                    normal_tmin_celsius=item["tmin"],
                    extreme_heat_days_p90=item["heat_days"],
                    dry_spell_frequency=item["dry_freq"],
                    heavy_rain_days_count=2.0 if item["rainfall"] > 100.0 else 0.5,
                    baseline_period="1991-2020",
                )
                db.add(baseline)
            db.commit()
            records = list(db.execute(stmt).scalars().all())

        return [ClimateBaselineResponse.model_validate(r) for r in records]

    @staticmethod
    def assess_exposure(
        db: Session,
        request: ClimateExposureAssessmentRequest,
    ) -> ClimateExposureAssessment:
        plot = db.get(Plot, request.plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        # Determine Hazard and Vulnerability based on forecast and crop stage
        tmax = request.forecast_tmax or 35.0
        rain7d = request.forecast_rainfall_next_7_days or 0.0
        dry_days = request.consecutive_rainless_days or 0
        stage = request.crop_stage.upper()

        hazard = "NORMAL_CONDITIONS"
        severity = "LOW"
        vuln_score = 0.25
        recommendation = "Standard agronomic maintenance according to seasonal calendar."
        citation = "PJTSAU / ICAR Standard Guidelines"

        is_reproductive = any(k in stage for k in ["FLOWER", "BOLL", "PANICLE", "FRUIT", "GRAIN"])

        if dry_days >= 14 or (dry_days >= 10 and rain7d < 5.0):
            hazard = "DRY_SPELL"
            if is_reproductive:
                severity = "CRITICAL" if dry_days >= 16 else "HIGH"
                vuln_score = 0.85 if dry_days >= 16 else 0.72
                recommendation = (
                    "Apply foliar spray of 1% Potassium Nitrate (KNO3) or 2% DAP to mitigate "
                    "flower/boll shedding; implement alternate-furrow life-saving irrigation."
                )
                citation = "PJTSAU Kharif Contingency Advisory / ICAR-CRIDA"
            else:
                severity = "MODERATE"
                vuln_score = 0.55
                recommendation = "Inter-cultivation to create dust mulch and break soil capillarity; life-saving irrigation."
                citation = "ICAR-CRIDA Dryland Contingency Manual"
        elif tmax >= 38.0:
            hazard = "HEAT_STRESS"
            if is_reproductive:
                severity = "CRITICAL" if tmax >= 40.0 else "HIGH"
                vuln_score = 0.82
                recommendation = (
                    "Maintain light frequent irrigations in evening hours; spray 0.5% zinc sulphate + "
                    "1% urea to alleviate thermal respiration loss."
                )
                citation = "PJTSAU Heat Mitigation Protocol"
            else:
                severity = "MODERATE"
                vuln_score = 0.50
                recommendation = "Maintain soil moisture to reduce ground radiant heat."
                citation = "ICAR-CRIDA Thermal Advisory"
        elif rain7d >= 100.0:
            hazard = "WATERLOGGING"
            severity = "HIGH" if is_reproductive else "MODERATE"
            vuln_score = 0.75 if is_reproductive else 0.60
            recommendation = (
                "Open dead furrows and clear drainage outlets immediately. "
                "Foliar spray of 1% urea after water recedes to revive root uptake."
            )
            citation = "PJTSAU Waterlogging Drainage Protocol"

        assessment = ClimateExposureAssessment(
            plot_id=request.plot_id,
            crop_id=request.crop_id,
            hazard_type=hazard,
            severity_level=severity,
            crop_stage=request.crop_stage,
            vulnerability_score=vuln_score,
            forecast_tmax=request.forecast_tmax,
            forecast_rainfall_next_7_days=request.forecast_rainfall_next_7_days,
            consecutive_rainless_days=request.consecutive_rainless_days,
            recommended_adaptation=recommendation,
            institutional_citation=citation,
            assessed_at=datetime.now(timezone.utc),
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Add adaptation scenario
        scenario = ClimateAdaptationScenario(
            assessment_id=assessment.id,
            title="PJTSAU Protective Foliar & Drainage Package",
            description=recommendation,
            projected_loss_reduction_percent=42.0 if severity in ["HIGH", "CRITICAL"] else 20.0,
            cost_delta_inr=650.0,
            intervention_actions_json=json.dumps([
                {"action": "Foliar Nutrition", "material": "1% KNO3", "timing": "Immediate"},
                {"action": "Soil Conservation", "material": "Inter-row Mulch", "timing": "Within 48h"},
            ]),
        )
        db.add(scenario)
        db.commit()
        db.refresh(assessment)
        return assessment
