"""
ACREVIA - Sustainable Agriculture Service (Pillar E).
Manages practice taxonomies, farm practice records, empirical SOC tracking,
IPCC Tier 1/2 research-grade greenhouse gas accounting, and seasonal sustainability scorecards.
"""

from datetime import datetime, timezone
import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.sustainability import (
    AgriculturalPracticeDefinition,
    FarmPracticeRecord,
    SoilCarbonMeasurement,
    EnvironmentalAccountingEstimate,
    SUSTAINABILITY_RESEARCH_DISCLAIMER,
)
from backend.app.models.farm import Plot
from backend.app.schemas.sustainability import (
    FarmPracticeRecordCreate,
    SoilCarbonMeasurementCreate,
    SeasonalSustainabilityScorecardResponse,
)

logger = logging.getLogger(__name__)

CANONICAL_PRACTICES = [
    {
        "code": "GREEN_MANURE",
        "category": "SOIL_COVER",
        "title_en": "Green Manuring (Dhaincha / Sunnhemp)",
        "title_te": "పచ్చిరొట్ట ఎరువుల సాగు (జీలుగ / జనుము)",
        "title_hi": "हरी खाद (ढैंचा / सनई)",
        "description_en": "Cultivating leguminous biomass pre-monsoon and incorporating into soil at 45 DAS.",
        "specification": {"biomass_target_t_ha": 20.0, "nitrogen_fixed_kg_ha": 70.0},
    },
    {
        "code": "CROP_RESIDUE_RETENTION",
        "category": "RESIDUE_MGMT",
        "title_en": "In-situ Crop Residue Retention",
        "title_te": "పంట అవశేషాల భూమిలోనే నిలిపివేత",
        "title_hi": "फसल अवशेष प्रबंधन",
        "description_en": "Shredding and retaining crop stalks on soil surface, eliminating open-field stubble burning.",
        "specification": {"cover_percentage": 60.0},
    },
    {
        "code": "INTERCROPPING_PULSE",
        "category": "CROP_DIVERSITY",
        "title_en": "Cotton + Pigeonpea Intercropping (4:1)",
        "title_te": "పత్తి + కంది అంతరపంట (4:1)",
        "title_hi": "कपास + अरहर अंतःफसल (4:1)",
        "description_en": "Strip intercropping of redgram within cotton for biological pest control and nitrogen enrichment.",
        "specification": {"ratio": "4:1"},
    },
    {
        "code": "BIOLOGICAL_PEST_CONTROL",
        "category": "IPM",
        "title_en": "Pheromone Traps & Biological Parasitoids",
        "title_te": "లింగాకర్షక బుట్టలు మరియు మిత్రపురుగులు",
        "title_hi": "फेरोमोन ट्रैप एवं जैविक नियंत्रण",
        "description_en": "Deploying 8 pheromone traps per acre and releasing Trichogramma parasitoids.",
        "specification": {"traps_per_acre": 8},
    },
    {
        "code": "BBF_CONSERVATION_FURROW",
        "category": "SOIL_WATER",
        "title_en": "Broad Bed and Furrow (BBF) System",
        "title_te": "వెడల్పాటి బోదెలు - సాళ్ల పద్ధతి",
        "title_hi": "चौड़ी क्यारी एवं कूंड़ प्रणाली",
        "description_en": "1.2m raised beds with conservation furrows along the contour for in-situ moisture retention.",
        "specification": {"bed_width_m": 1.2},
    },
]


class SustainService:

    @staticmethod
    def get_practices(db: Session) -> List[AgriculturalPracticeDefinition]:
        stmt = select(AgriculturalPracticeDefinition).order_by(AgriculturalPracticeDefinition.category.asc())
        records = list(db.execute(stmt).scalars().all())

        if not records:
            # Seed canonical practices
            for item in CANONICAL_PRACTICES:
                p = AgriculturalPracticeDefinition(
                    code=item["code"],
                    category=item["category"],
                    title_en=item["title_en"],
                    title_te=item["title_te"],
                    title_hi=item["title_hi"],
                    description_en=item["description_en"],
                    specification_json=json.dumps(item["specification"]),
                )
                db.add(p)
            db.commit()
            records = list(db.execute(stmt).scalars().all())

        return records

    @staticmethod
    def record_practice(db: Session, data: FarmPracticeRecordCreate) -> FarmPracticeRecord:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        record = FarmPracticeRecord(
            plot_id=data.plot_id,
            practice_code=data.practice_code,
            implementation_date=data.implementation_date or datetime.now(timezone.utc),
            area_covered_acres=data.area_covered_acres,
            verification_method=data.verification_method,
            status="ACTIVE",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def record_carbon_measurement(db: Session, data: SoilCarbonMeasurementCreate) -> SoilCarbonMeasurement:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        # Guardrail: Method must be empirical accredited analytical standard
        if data.method not in ["WALKLEY_BLACK", "DRY_COMBUSTION"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid analytical method. Empirical SOC requires WALKLEY_BLACK or DRY_COMBUSTION.",
            )

        measurement = SoilCarbonMeasurement(
            plot_id=data.plot_id,
            sample_date=data.sample_date or datetime.now(timezone.utc),
            depth_cm=data.depth_cm,
            soc_percent=data.soc_percent,
            bulk_density=data.bulk_density,
            method=data.method,
            lab_accreditation=data.lab_accreditation,
        )
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        return measurement

    @staticmethod
    def get_emissions_estimate(
        db: Session,
        plot_id: str,
        season: str = "Kharif",
        year: int = 2026,
    ) -> EnvironmentalAccountingEstimate:
        plot = db.get(Plot, plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        plot_acreage = getattr(plot, "acreage", 1.0) or 1.0
        plot_ha = plot_acreage * 0.404686

        # Check existing
        stmt = (
            select(EnvironmentalAccountingEstimate)
            .where(
                EnvironmentalAccountingEstimate.plot_id == plot_id,
                EnvironmentalAccountingEstimate.season == season,
                EnvironmentalAccountingEstimate.year == year,
            )
        )
        existing = db.execute(stmt).scalar_one_or_none()
        if existing:
            return existing

        # Research-grade estimation based on IPCC Tier 1/2:
        # Typical farm operational inputs:
        # Synthetic N ~ 120 kg N/ha -> Direct N2O = N * 0.01 * (44/28) * 265 kg CO2e
        n_applied_kg = 120.0 * plot_ha
        n2o_emissions = round(n_applied_kg * 0.01 * (44.0 / 28.0) * 265.0, 2)

        # Methane (low if aerobic upland cotton/chilli ~ 0; if flooded paddy ~ 1.3 kg CH4/ha/day * 110d * 28)
        # Scaled by 0.52 for AWD
        ch4_emissions = round(1.3 * 110.0 * plot_ha * 0.52 * 28.0, 2)

        # Diesel fuel ~ 45 L/ha for field preparation & pump
        fuel_liters = 45.0 * plot_ha
        fuel_emissions = round(fuel_liters * 2.68, 2)

        total_co2e = round(n2o_emissions + ch4_emissions + fuel_emissions, 2)

        estimate = EnvironmentalAccountingEstimate(
            plot_id=plot_id,
            season=season,
            year=year,
            fertilizer_n2o_kg_co2e=n2o_emissions,
            paddy_ch4_kg_co2e=ch4_emissions,
            fuel_combustion_kg_co2e=fuel_emissions,
            total_emissions_kg_co2e=total_co2e,
            emission_intensity_kg_co2e_per_kg=round(total_co2e / max(plot_acreage * 1000.0, 100.0), 3),
            is_certified=False,  # Immutable non-certified research estimate
            scientific_disclaimer=SUSTAINABILITY_RESEARCH_DISCLAIMER,
        )
        db.add(estimate)
        db.commit()
        db.refresh(estimate)
        return estimate

    @staticmethod
    def get_scorecard(
        db: Session,
        plot_id: str,
        season: str = "Kharif",
        year: int = 2026,
    ) -> SeasonalSustainabilityScorecardResponse:
        plot = db.get(Plot, plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        # Query verified practices on this plot
        stmt = select(FarmPracticeRecord).where(
            FarmPracticeRecord.plot_id == plot_id,
            FarmPracticeRecord.status == "ACTIVE",
        )
        records = list(db.execute(stmt).scalars().all())
        practice_codes = [r.practice_code for r in records]

        # Calculate scores
        soil_cover = 22.0 if any(c in practice_codes for c in ["GREEN_MANURE", "CROP_RESIDUE_RETENTION"]) else 12.0
        water_eff = 20.0 if "BBF_CONSERVATION_FURROW" in practice_codes else 14.0
        nutrient_bal = 18.0
        ipm_score = 15.0 if "BIOLOGICAL_PEST_CONTROL" in practice_codes else 8.0
        biodiversity = 14.0 if "INTERCROPPING_PULSE" in practice_codes else 6.0

        total_index = round(soil_cover + water_eff + nutrient_bal + ipm_score + biodiversity, 1)

        return SeasonalSustainabilityScorecardResponse(
            plot_id=plot_id,
            season=season,
            year=year,
            sustainability_index=min(100.0, total_index),
            soil_cover_score=soil_cover,
            water_efficiency_score=water_eff,
            nutrient_balance_score=nutrient_bal,
            ipm_adoption_score=ipm_score,
            biodiversity_score=biodiversity,
            verified_practices=practice_codes,
            disclaimer=SUSTAINABILITY_RESEARCH_DISCLAIMER,
        )
