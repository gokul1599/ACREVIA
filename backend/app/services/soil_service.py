"""
ACREVIA - Soil Health Intelligence Service (Pillar A).
Manages soil pedon profiles, field samples, accredited lab results, spatial coverage density checks,
and longitudinal soil organic carbon / nutrient history.
"""

from datetime import datetime, timezone
import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.soil_health import SoilProfile, SoilSample, SoilTestResult
from backend.app.models.farm import Plot
from backend.app.schemas.soil_health import (
    SoilProfileCreate,
    SoilSampleCreate,
    SoilTestResultCreate,
    SoilPlotHistoryResponse,
    SoilTestResultResponse,
)

logger = logging.getLogger(__name__)


class SoilService:

    @staticmethod
    def create_profile(db: Session, data: SoilProfileCreate) -> SoilProfile:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        profile = SoilProfile(
            plot_id=data.plot_id,
            soil_order=data.soil_order,
            soil_series_name=data.soil_series_name,
            drainage_class=data.drainage_class,
            bulk_density_g_cm3=data.bulk_density_g_cm3,
            effective_soil_depth_cm=data.effective_soil_depth_cm,
            texture_class=data.texture_class,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def create_sample(db: Session, user_id: str, data: SoilSampleCreate) -> SoilSample:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        # Check existing code
        existing = db.execute(select(SoilSample).where(SoilSample.sample_code == data.sample_code)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Soil sample code already exists")

        # Spatial coverage density check:
        # Minimum recommended is 1 composite sample (at least 5 cores) per 2.5 acres.
        # If plot acreage > 2.5 and composite cores < 5, or if sampling density is sparse:
        warning = None
        plot_acreage = getattr(plot, "acreage", 2.0) or 2.0
        if plot_acreage > 2.5 and data.composite_cores_count < 5:
            warning = "INSUFFICIENT_SPATIAL_COVERAGE"
        elif plot_acreage > 5.0 and data.composite_cores_count < 8:
            warning = "INSUFFICIENT_SPATIAL_COVERAGE"

        sample = SoilSample(
            plot_id=data.plot_id,
            profile_id=data.profile_id,
            sampled_by_user_id=user_id,
            sample_code=data.sample_code,
            sampling_date=data.sampling_date or datetime.now(timezone.utc),
            sampling_depth_min_cm=data.sampling_depth_min_cm,
            sampling_depth_max_cm=data.sampling_depth_max_cm,
            gps_latitude=data.gps_latitude,
            gps_longitude=data.gps_longitude,
            composite_cores_count=data.composite_cores_count,
            spatial_coverage_warning=warning,
            status="COLLECTED",
        )
        db.add(sample)
        db.commit()
        db.refresh(sample)
        return sample

    @staticmethod
    def ingest_lab_result(db: Session, data: SoilTestResultCreate) -> SoilTestResult:
        sample = db.get(SoilSample, data.soil_sample_id)
        if not sample:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Soil sample not found")

        provenance_payload = data.provenance or {
            "source": "ACCREDITED_LAB",
            "laboratory": data.laboratory_name,
            "accreditation": data.accreditation_number,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }

        result = SoilTestResult(
            soil_sample_id=data.soil_sample_id,
            laboratory_name=data.laboratory_name,
            accreditation_number=data.accreditation_number,
            ph=data.ph,
            electrical_conductivity_ec=data.electrical_conductivity_ec,
            organic_carbon_percent=data.organic_carbon_percent,
            available_nitrogen_kg_ha=data.available_nitrogen_kg_ha,
            available_phosphorus_kg_ha=data.available_phosphorus_kg_ha,
            available_potassium_kg_ha=data.available_potassium_kg_ha,
            available_sulphur_ppm=data.available_sulphur_ppm,
            available_zinc_ppm=data.available_zinc_ppm,
            available_iron_ppm=data.available_iron_ppm,
            available_boron_ppm=data.available_boron_ppm,
            provenance_json=json.dumps(provenance_payload),
            verified_at=datetime.now(timezone.utc),
        )
        sample.status = "ANALYZED"
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def get_plot_history(db: Session, plot_id: str) -> SoilPlotHistoryResponse:
        plot = db.get(Plot, plot_id)
        if not plot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")

        # Fetch samples and corresponding lab results
        stmt = (
            select(SoilTestResult)
            .join(SoilSample, SoilTestResult.soil_sample_id == SoilSample.id)
            .where(SoilSample.plot_id == plot_id)
            .order_by(SoilTestResult.created_at.asc())
        )
        test_records = list(db.execute(stmt).scalars().all())

        soc_trend = 0.0
        latest_ph = None
        latest_n_status = "UNKNOWN"

        if test_records:
            first_soc = test_records[0].organic_carbon_percent
            latest_record = test_records[-1]
            latest_soc = latest_record.organic_carbon_percent
            soc_trend = round(latest_soc - first_soc, 3)
            latest_ph = latest_record.ph

            n_val = latest_record.available_nitrogen_kg_ha
            if n_val < 280.0:
                latest_n_status = "DEFICIENT"
            elif n_val <= 560.0:
                latest_n_status = "SUFFICIENT"
            else:
                latest_n_status = "EXCESS"

        return SoilPlotHistoryResponse(
            plot_id=plot_id,
            samples_count=len(test_records),
            results=[SoilTestResultResponse.model_validate(r) for r in test_records],
            soc_trend_percent=soc_trend,
            latest_ph=latest_ph,
            latest_nitrogen_status=latest_n_status,
        )
