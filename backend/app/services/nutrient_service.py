"""
ACREVIA - Nutrient Intelligence & Governance Service (Pillar D).
Generates soil-test-driven N-P-K & micronutrient prescriptions according to PJTSAU standards,
enforces strict upper-bound safety guards, and manages expert agronomist escalations.
"""

from datetime import datetime, timezone
import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.nutrient_intelligence import NutrientAssessment, NutrientExpertReview
from backend.app.models.soil_health import SoilTestResult
from backend.app.models.crop import Crop
from backend.app.schemas.nutrient_intelligence import (
    NutrientPrescribeRequest,
    NutrientExpertReviewRequest,
    SplitScheduleItem,
)

logger = logging.getLogger(__name__)

# Institutional Upper Bounds (kg/ha)
DOSAGE_UPPER_BOUNDS = {
    "COTTON": {"n": 180.0, "p2o5": 90.0, "k2o": 90.0},
    "RICE": {"n": 160.0, "p2o5": 80.0, "k2o": 60.0},
    "CHILLI": {"n": 220.0, "p2o5": 90.0, "k2o": 180.0},
    "DEFAULT": {"n": 200.0, "p2o5": 90.0, "k2o": 120.0},
}


class NutrientService:

    @staticmethod
    def prescribe_nutrients(db: Session, request: NutrientPrescribeRequest) -> NutrientAssessment:
        soil_test = db.get(SoilTestResult, request.soil_test_result_id)
        if not soil_test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soil test result not found")

        crop = db.get(Crop, request.crop_id)
        crop_name = crop.name_en.upper() if crop else "COTTON"

        # Determine dosage boundary limits
        limits = DOSAGE_UPPER_BOUNDS.get("DEFAULT")
        for key in ["COTTON", "RICE", "CHILLI"]:
            if key in crop_name:
                limits = DOSAGE_UPPER_BOUNDS[key]
                break

        # Safety Check: Enforce rejection of excessive unsupported dosages
        if request.override_n_kg_ha is not None and request.override_n_kg_ha > limits["n"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"UNACCEPTABLE_DOSAGE_OVERRIDE: Requested nitrogen dose ({request.override_n_kg_ha} kg/ha) exceeds safe institutional threshold ({limits['n']} kg/ha) for {crop_name}.",
            )

        # Baseline PJTSAU Recommended Doses (kg/ha)
        base_n = 120.0
        base_p = 60.0
        base_k = 60.0
        citation = "PJTSAU Package of Practices (Telangana Agricultural Almanac)"

        if "RICE" in crop_name:
            base_n, base_p, base_k = 120.0, 60.0, 40.0
        elif "CHILLI" in crop_name:
            base_n, base_p, base_k = 150.0, 60.0, 120.0

        # Macronutrient Sufficiency Classification & Adjustments
        # Available N
        n_val = soil_test.available_nitrogen_kg_ha
        if n_val < 280.0:
            n_status = "DEFICIENT"
            rec_n = base_n * 1.20
        elif n_val <= 560.0:
            n_status = "SUFFICIENT"
            rec_n = base_n
        else:
            n_status = "EXCESS"
            rec_n = base_n * 0.75

        # Available P2O5
        p_val = soil_test.available_phosphorus_kg_ha
        if p_val < 22.0:
            p_status = "DEFICIENT"
            rec_p = base_p * 1.25
        elif p_val <= 55.0:
            p_status = "SUFFICIENT"
            rec_p = base_p
        else:
            p_status = "EXCESS"
            rec_p = base_p * 0.75

        # Available K2O
        k_val = soil_test.available_potassium_kg_ha
        if k_val < 140.0:
            k_status = "DEFICIENT"
            rec_k = base_k * 1.25
        elif k_val <= 330.0:
            k_status = "SUFFICIENT"
            rec_k = base_k
        else:
            k_status = "EXCESS"
            rec_k = base_k * 0.80

        # Cap recommendations to safe institutional bounds
        rec_n = min(round(rec_n, 1), limits["n"])
        rec_p = min(round(rec_p, 1), limits["p2o5"])
        rec_k = min(round(rec_k, 1), limits["k2o"])

        # Micronutrient checks
        zn_status = "DEFICIENT" if (soil_test.available_zinc_ppm or 1.0) < 0.60 else "SUFFICIENT"
        b_status = "DEFICIENT" if (soil_test.available_boron_ppm or 1.0) < 0.50 else "SUFFICIENT"

        micronutrient_recs = []
        if zn_status == "DEFICIENT":
            micronutrient_recs.append("Soil application of Zinc Sulphate (ZnSO4) @ 25 kg/ha basally; do not mix with phosphatic fertilizers.")
        if b_status == "DEFICIENT":
            micronutrient_recs.append("Foliar application of Solubor/Borax @ 1.5 g/L at square/flowering stage.")
        if soil_test.ph < 6.0:
            micronutrient_recs.append("Soil acidity detected: apply agricultural lime or dolomite based on buffer pH.")
        elif soil_test.ph > 8.5:
            micronutrient_recs.append("Soil alkalinity detected: apply gypsum @ 2-5 t/ha followed by leaching.")

        # Split Application Schedules
        schedule = []
        if "COTTON" in crop_name:
            schedule = [
                {"stage": "BASAL", "n_kg": round(rec_n * 0.20, 1), "p2o5_kg": rec_p, "k2o_kg": round(rec_k * 0.30, 1), "timing": "At sowing"},
                {"stage": "VEGETATIVE", "n_kg": round(rec_n * 0.30, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.20, 1), "timing": "30 DAS"},
                {"stage": "SQUARE_FORMATION", "n_kg": round(rec_n * 0.30, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.30, 1), "timing": "60 DAS"},
                {"stage": "BOLL_DEVELOPMENT", "n_kg": round(rec_n * 0.20, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.20, 1), "timing": "90 DAS"},
            ]
        elif "RICE" in crop_name:
            schedule = [
                {"stage": "BASAL", "n_kg": round(rec_n * 0.33, 1), "p2o5_kg": rec_p, "k2o_kg": round(rec_k * 0.50, 1), "timing": "Final puddling"},
                {"stage": "ACTIVE_TILLERING", "n_kg": round(rec_n * 0.34, 1), "p2o5_kg": 0.0, "k2o_kg": 0.0, "timing": "20-25 DAT"},
                {"stage": "PANICLE_INITIATION", "n_kg": round(rec_n * 0.33, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.50, 1), "timing": "40-45 DAT"},
            ]
        else:  # Chilli / general
            schedule = [
                {"stage": "BASAL", "n_kg": round(rec_n * 0.20, 1), "p2o5_kg": rec_p, "k2o_kg": round(rec_k * 0.20, 1), "timing": "Before transplanting"},
                {"stage": "VEGETATIVE", "n_kg": round(rec_n * 0.25, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.25, 1), "timing": "30 DAT"},
                {"stage": "FLOWERING_FRUITING", "n_kg": round(rec_n * 0.30, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.30, 1), "timing": "60 DAT"},
                {"stage": "MULTI_PICKING", "n_kg": round(rec_n * 0.25, 1), "p2o5_kg": 0.0, "k2o_kg": round(rec_k * 0.25, 1), "timing": "90-120 DAT"},
            ]

        assessment = NutrientAssessment(
            soil_test_result_id=request.soil_test_result_id,
            crop_id=request.crop_id,
            nitrogen_status=n_status,
            phosphorus_status=p_status,
            potassium_status=k_status,
            zinc_status=zn_status,
            boron_status=b_status,
            recommended_n_kg_ha=rec_n,
            recommended_p2o5_kg_ha=rec_p,
            recommended_k2o_kg_ha=rec_k,
            split_application_schedule_json=json.dumps(schedule),
            micronutrient_recommendations_json=json.dumps(micronutrient_recs),
            safeguard_checks_passed=True,
            institutional_citation=citation,
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        # Trigger automatic agronomist review if severe soil anomalies exist
        if soil_test.ph < 5.5 or soil_test.ph > 8.5 or soil_test.electrical_conductivity_ec > 2.0:
            expert_review = NutrientExpertReview(
                nutrient_assessment_id=assessment.id,
                expert_user_id="SYSTEM_AGRONOMIST_QUEUE",
                review_status="PENDING",
                agronomist_notes=f"Auto-escalated due to extreme soil chemical reading: pH={soil_test.ph}, EC={soil_test.electrical_conductivity_ec} dS/m.",
            )
            db.add(expert_review)
            db.commit()

        return assessment

    @staticmethod
    def get_assessment(db: Session, assessment_id: str) -> NutrientAssessment:
        assessment = db.get(NutrientAssessment, assessment_id)
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrient assessment not found")
        return assessment

    @staticmethod
    def submit_expert_review(
        db: Session,
        expert_user_id: str,
        request: NutrientExpertReviewRequest,
    ) -> NutrientExpertReview:
        assessment = db.get(NutrientAssessment, request.nutrient_assessment_id)
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrient assessment not found")

        revised_json = json.dumps(request.revised_prescription) if request.revised_prescription else None

        review = NutrientExpertReview(
            nutrient_assessment_id=request.nutrient_assessment_id,
            expert_user_id=expert_user_id,
            review_status=request.review_status,
            agronomist_notes=request.agronomist_notes,
            revised_prescription_json=revised_json,
            reviewed_at=datetime.now(timezone.utc),
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review
